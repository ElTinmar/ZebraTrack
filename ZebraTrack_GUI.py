# tracker gui

import sys
from PyQt5.QtWidgets import QApplication
from tracker import (
    AssignmentWidget, TrackerWidget, AnimalTrackerWidget, 
    BodyTrackerWidget, EyesTrackerWidget, TailTrackerWidget
)
from gui import ZebraTrackGUI

app = QApplication(sys.argv)

fish_tracker = TrackerWidget(
    AnimalTrackerWidget(assignment_widget=AssignmentWidget()),
    BodyTrackerWidget(),
    EyesTrackerWidget(),
    TailTrackerWidget()
)
'''
fish_tracker = TrackerWidget(
    AssignmentWidget(), 
    AnimalTrackerWidget(),
    None,
    None,
    None
)
'''

window = ZebraTrackGUI([fish_tracker])
sys.exit(app.exec())