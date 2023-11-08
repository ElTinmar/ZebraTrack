# tracker gui

import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from tracker import AssignmentWidget, TrackerWidget, AnimalTrackerWidget, BodyTrackerWidget, EyesTrackerWidget,TailTrackerWidget
from gui import ZebraTrackGUI

app = QApplication(sys.argv)

fish_tracker = TrackerWidget(
    AssignmentWidget(), 
    AnimalTrackerWidget(),
    BodyTrackerWidget(),
    EyesTrackerWidget(),
    TailTrackerWidget()
)

paramecia_tracker = TrackerWidget(
    AssignmentWidget(), 
    AnimalTrackerWidget(),
    BodyTrackerWidget(),
    None,
    None,
)

window = ZebraTrackGUI([fish_tracker, paramecia_tracker])
sys.exit(app.exec())