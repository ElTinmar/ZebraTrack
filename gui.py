from widgets.animal_tracker import AnimalTrackerWidget
from widgets.body_tracker import BodyTrackerWidget
from widgets.eye_tracker import EyesTrackerWidget
from widgets.tail_tracker import TailTrackerWidget 
from trackers.tracker import Tracker
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QStackedLayout, QDockWidget
from typing import Protocol
from image.imconvert import im2gray, im2single

# TODO add a media control bar with play / pause, frame by frame forward and backwards
# and slider  

class VideoReader(Protocol):
    pass

class Background(Protocol):
    pass

class Assignment(Protocol):
    pass

class TrackerThreshold(QMainWindow):

    def __init__(
            self, 
            reader: VideoReader, 
            background: Background, 
            assignment: Assignment, 
            *args, **kwargs
        ) -> None:

        super().__init__(*args, **kwargs)
        self.reader = reader
        self.background = background
        self.assignment = assignment
        self.tracker = None
        self.declare_components()
        self.layout_components()

        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)
        self.timer.start()
        self.show()

    def declare_components(self):
        self.animal_tracker_widget = AnimalTrackerWidget(self)
        self.body_tracker_widget = BodyTrackerWidget(self)
        self.eyes_tracker_widget = EyesTrackerWidget(self)
        self.tail_tracker_widget = TailTrackerWidget(self)

    def layout_components(self):
        dock_widget = QDockWidget('Single Animal', self)
        stackedlayout = QStackedLayout()
        stackedlayout.addWidget(self.body_tracker_widget)
        stackedlayout.addWidget(self.eyes_tracker_widget)
        stackedlayout.addWidget(self.tail_tracker_widget)      
        dock_widget.setLayout(stackedlayout)  
        
        mainlayout = QHBoxLayout()
        mainlayout.addWidget(self.animal_tracker_widget)
        mainlayout.addLayout(stackedlayout)

        self.setCentralWidget(self.animal_tracker_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    def update_tracker(self):
        self.animal_tracker_widget.update_tracker()
        self.body_tracker_widget.update_tracker()
        self.eyes_tracker_widget.update_tracker()
        self.tail_tracker_widget.update_tracker()
        self.tracker = Tracker(
            self.assignment,
            None,
            self.animal_tracker_widget.tracker,
            self.body_tracker_widget.tracker,
            self.eyes_tracker_widget.tracker,
            self.tail_tracker_widget.tracker
        )

    def loop(self):
        self.update_tracker()
        ret, image = self.reader.next_frame()
        if not ret:
            self.reader.reset_reader()
            return
        image_gray = im2single(im2gray(image))
        image_sub = self.background.subtract_background(image_gray)
        tracking = self.tracker.track(image_sub)
        self.display(tracking)

    def display(self, tracking):
        id = 0 # TODO implement mouse callback
        self.animal_tracker_widget.display(tracking['animal'])
        self.body_tracker_widget.display(tracking['body'][id])
        self.eyes_tracker_widget.display(tracking['eyes'][id])
        self.tail_tracker_widget.display(tracking['tail'][id])