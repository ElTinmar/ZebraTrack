from gui.tracker import TrackerWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout
from typing import List, Protocol
from image.imconvert import im2gray, im2single
from video.background_widget import BackgroundSubtractorWidget
from video.playlist_widget import PlaylistWidget

# TODO add a media control bar with play / pause, frame by frame forward and backwards
# and slider  

# TODO add tabs to load file into a list
# TODO add tab to select background subtraction methods and options
# TODO add the possibility to dynamically add trackers in a new tab
# TODO remove parameters from init, load everything from the GUI

class VideoReader(Protocol):
    pass

class Background(Protocol):
    pass

class ZebraTrackGUI(QMainWindow):

    def __init__(
            self, 
            reader: VideoReader,
            background: Background,
            trackers: List[TrackerWidget], 
            *args, **kwargs
        ) -> None:

        super().__init__(*args, **kwargs)
        self.setWindowTitle('ZebraTrack')

        self.reader = reader
        self.background = background
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

    def layout_components(self):
        main_widget = QWidget()

        video_control = QVBoxLayout()
        video_control.addWidget(self.playlist_widget)
        video_control.addWidget(self.background_widget)

        tabs = QTabWidget() 
        for tracker in self.trackers:
            tabs.addTab(tracker,'tracker')

        main_layout = QHBoxLayout(main_widget)
        main_layout.addLayout(video_control)
        main_layout.addWidget(tabs)

        self.setCentralWidget(main_widget)

    def update_background(self):
        # update background subtraction method
        pass

    def update_tracker(self):
        for tracker in self.trackers:
            tracker.update_tracker()

    def loop(self):
        self.update_tracker()
        self.update_background()
        ret, image = self.reader.next_frame()
        if not ret:
            self.reader.reset_reader()
            return
        image_gray = im2single(im2gray(image))
        image_sub = self.background.subtract_background(image_gray)
        for tracker in self.trackers:
            tracking = tracker.tracker.track(image_sub)
            tracker.display(tracking)