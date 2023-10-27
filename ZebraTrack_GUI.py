# tracker gui

import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from tracker import LinearSumAssignment, GridAssignment, TrackerWidget, AnimalTrackerWidget, BodyTrackerWidget, EyesTrackerWidget,TailTrackerWidget
from gui import ZebraTrackGUI

#assignment = LinearSumAssignment(distance_threshold=50)
#LUT = np.hstack(( np.zeros((600,600)) , np.ones((600,600)) ))
X,Y = np.meshgrid(np.arange(1800) // 600,np.arange(1800) // 600)
LUT = X + 3*Y

app = QApplication(sys.argv)

fish_tracker = TrackerWidget(
    GridAssignment(LUT), 
    AnimalTrackerWidget(),
    BodyTrackerWidget(),
    EyesTrackerWidget(),
    TailTrackerWidget()
)

paramecia_tracker = TrackerWidget(
    LinearSumAssignment(distance_threshold=10), 
    AnimalTrackerWidget(),
    BodyTrackerWidget(),
    None,
    None,
)

window = ZebraTrackGUI([fish_tracker, paramecia_tracker])
sys.exit(app.exec())