from widgets.animal_tracker import AnimalTrackerWidget
from widgets.body_tracker import BodyTrackerWidget
from widgets.eye_tracker import EyesTrackerWidget
from widgets.tail_tracker import TailTrackerWidget 
from trackers.tracker import Tracker
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QDockWidget
from typing import Protocol, Optional

# TODO add a media control bar with play / pause, frame by frame forward and backwards
# and slider  

class Assignment(Protocol):
    pass

class TrackerWidget(QMainWindow):

    def __init__(
            self, 
            assignment: Assignment, 
            animal_tracker_widget: AnimalTrackerWidget,
            body_tracker_widget: Optional[BodyTrackerWidget],
            eyes_tracker_widget: Optional[EyesTrackerWidget],
            tail_tracker_widget: Optional[TailTrackerWidget],
            *args, **kwargs
        ) -> None:

        super().__init__(*args, **kwargs)
        self.assignment = assignment
        self.animal_tracker_widget = animal_tracker_widget
        self.body_tracker_widget = body_tracker_widget
        self.eyes_tracker_widget = eyes_tracker_widget
        self.tail_tracker_widget = tail_tracker_widget
        self.tracker = None
        self.layout_components()

    def layout_components(self):
        if self.body_tracker_widget is not None:
            dock_widget = QDockWidget('Single Animal', self)
            tabs = QTabWidget()
            tabs.addTab(self.body_tracker_widget, 'body')
            if self.eyes_tracker_widget is not None:
                tabs.addTab(self.eyes_tracker_widget, 'eyes')
            if self.tail_tracker_widget is not None:
                tabs.addTab(self.tail_tracker_widget, 'tail')      
            dock_widget.setWidget(tabs)  
            dock_widget.setFixedHeight(800)
            self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        self.setCentralWidget(self.animal_tracker_widget)
        self.setFixedHeight(800)
        
    def update_tracker(self):
        body_tracker = None
        eyes_tracker = None
        tail_tracker = None
        self.animal_tracker_widget.update_tracker()
        animal_tracker = self.animal_tracker_widget.tracker
        if self.body_tracker_widget is not None:
            self.body_tracker_widget.update_tracker()
            body_tracker = self.body_tracker_widget.tracker
        if self.eyes_tracker_widget is not None:
            self.eyes_tracker_widget.update_tracker()
            eyes_tracker = self.eyes_tracker_widget.tracker
        if self.tail_tracker_widget is not None:
            self.tail_tracker_widget.update_tracker()
            tail_tracker = self.tail_tracker_widget.tracker

        self.tracker = Tracker(
            self.assignment,
            None,
            animal_tracker,
            body_tracker,
            eyes_tracker,
            tail_tracker
        )

    def display(self, tracking):
        id = 0 # TODO implement mouse callback
        if tracking is not None:
            self.animal_tracker_widget.display(tracking['animals'])
            if self.body_tracker_widget is not None:
                self.body_tracker_widget.display(tracking['body'][id])
            if self.eyes_tracker_widget is not None:
                self.eyes_tracker_widget.display(tracking['eyes'][id])
            if self.tail_tracker_widget is not None:
                self.tail_tracker_widget.display(tracking['tail'][id])