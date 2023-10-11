from gui.tracker import TrackerWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from typing import List, Protocol
from image.imconvert import im2gray, im2single

# TODO add a media control bar with play / pause, frame by frame forward and backwards
# and slider  
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
        self.layout_components()

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)
        self.timer.start()
        self.show()

    def layout_components(self):
        tabs = QTabWidget() 
        for tracker in self.trackers:
            tabs.addTab(tracker,'tracker')
        self.setCentralWidget(tabs)

    def update_tracker(self):
        for tracker in self.trackers:
            tracker.update_tracker()

    def loop(self):
        self.update_tracker()
        ret, image = self.reader.next_frame()
        if not ret:
            self.reader.reset_reader()
            return
        image_gray = im2single(im2gray(image))
        image_sub = self.background.subtract_background(image_gray)
        for tracker in self.trackers:
            # TODO this is breaking encapsulation, fix this
            tracking = tracker.tracker.track(image_sub)
            tracker.display(tracking)