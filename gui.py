from widgets.animal_tracker import AnimalTrackerWidget
from widgets.body_tracker import BodyTrackerWidget
from widgets.eye_tracker import EyesTrackerWidget
from widgets.tail_tracker import TailTrackerWidget 
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from typing import Protocol

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
        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.animal_tracker_widget)
        mainlayout.addWidget(self.body_tracker_widget)
        mainlayout.addWidget(self.eyes_tracker_widget)
        mainlayout.addWidget(self.tail_tracker_widget)
        widget = QWidget()
        widget.setLayout(mainlayout)
        self.setCentralWidget(widget)

    def loop(self):
        ret, image = self.reader.next_frame()
        if not ret:
            self.reader.reset_reader()
            return
        image_gray = im2single(im2gray(image))
        bckg_sub = image_gray - self.bckg

        # TODO add a mouse callback to select which fish you want to show for body/eye/tail
        # TODO switch on/off overlay for different trackers on the global image

        self.animal_tracker_widget.set_image(bckg_sub)
        self.body_tracker_widget.set_image(bckg_sub)
        self.eyes_tracker_widget.set_image(bckg_sub)
        self.tail_tracker_widget.set_image(bckg_sub)