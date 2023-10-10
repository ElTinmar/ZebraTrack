from gui.animal_tracker import AnimalTrackerWidget
from gui.body_tracker import BodyTrackerWidget
from gui.eye_tracker import EyesTrackerWidget
from gui.tail_tracker import TailTrackerWidget 
from trackers.tracker import Tracker
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QDockWidget
from typing import Protocol, Optional
from scipy.spatial.distance import cdist
import numpy as np

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
        # TODO I'm breaking encapsulation, this needs to be fixed
        self.animal_tracker_widget.image_overlay.mousePressEvent = self.on_mouse_click
        self.body_tracker_widget = body_tracker_widget
        self.eyes_tracker_widget = eyes_tracker_widget
        self.tail_tracker_widget = tail_tracker_widget
        self.tracker = None
        self.current_id = 0
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
            self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)
        self.setCentralWidget(self.animal_tracker_widget)
        
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
        if tracking is not None:
            self.animal_tracker_widget.display(tracking['animals'])
            if self.body_tracker_widget is not None:
                self.body_tracker_widget.display(tracking['body'][self.current_id])
            if self.eyes_tracker_widget is not None:
                self.eyes_tracker_widget.display(tracking['eyes'][self.current_id])
            if self.tail_tracker_widget is not None:
                self.tail_tracker_widget.display(tracking['tail'][self.current_id])

    def on_mouse_click(self, event):
        x = event.pos().x()
        y = event.pos().y() 

        mouse_position = np.array([[x, y]])
        # TODO I'm breaking encapsulation again
        zoom = self.animal_tracker_widget.zoom.value()
        target_res = self.animal_tracker_widget.target_pix_per_mm.value()
        res = self.animal_tracker_widget.pix_per_mm.value()
        mouse_position = mouse_position * (100 * res) / (target_res * zoom)  

        centroids = self.assignment.get_centroids()
        ID = self.assignment.get_ID()
        dist = cdist(mouse_position, centroids)
        self.current_id = ID[np.argmin(dist)]