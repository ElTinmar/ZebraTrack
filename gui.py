from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout
from typing import List, Protocol
from tracker import TrackerWidget
from image_tools import im2gray, im2single
from video_tools import BackgroundSubtractorWidget, PlaylistWidget

# TODO add the possibility to dynamically add trackers in a new tab
# TODO remove parameters from init, load everything from the GUI

class VideoReader(Protocol):
    pass

class Background(Protocol):
    pass

class ZebraTrackGUI(QMainWindow):

    def __init__(
            self, 
            trackers: List[TrackerWidget], 
            *args, **kwargs
        ) -> None:

        super().__init__(*args, **kwargs)
        self.setWindowTitle('ZebraTrack')

        self.trackers = trackers
        self.create_components()
        self.layout_components()

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)
        self.timer.start()
        self.show()

    def create_components(self):
        self.playlist_widget = PlaylistWidget()
        self.background_widget = BackgroundSubtractorWidget()

        # connect widgets
        self.playlist_widget.video_selected_signal.connect(self.background_widget.set_video_file)
        for tracker in self.trackers:
            self.background_widget.background_initialized.connect(tracker.animal_tracker_widget.assignment_widget.set_background_image)
        
    def layout_components(self):
        main_widget = QWidget()

        video_control = QVBoxLayout()
        video_control.addWidget(self.playlist_widget)
        video_control.addWidget(self.background_widget)

        self.tabs = QTabWidget() 
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.on_tab_close)

        for tracker in self.trackers:
            self.tabs.addTab(tracker,'tracker')

        main_layout = QHBoxLayout(main_widget)
        main_layout.addLayout(video_control)
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(main_widget)

    def on_tab_close(self, index):
        self.trackers.pop(index)
        self.tabs.removeTab(index)

    def update_tracker(self):
        for tracker in self.trackers:
            tracker.update_tracker()

    def loop(self):
        self.update_tracker()
        background = self.background_widget.get_background_subtractor()
        reader = self.playlist_widget.get_video_reader()
        if reader.is_open():
            ret, image = reader.next_frame()
            if not ret:
                reader.reset_reader()
                return
            image_gray = im2single(im2gray(image))
            if background.is_initialized():
                image_sub = background.subtract_background(image_gray)
                for tracker in self.trackers:
                    if tracker is not None:
                        tracking = tracker.tracker.track(image_sub)
                        tracker.display(tracking)