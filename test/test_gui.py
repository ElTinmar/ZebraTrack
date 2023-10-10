import os
import socket
import pandas as pd
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

from video.video_reader import OpenCV_VideoReader
from video.background import StaticBackground, DynamicBackground, DynamicBackgroundMP
from trackers.assignment import LinearSumAssignment, GridAssignment
from gui.tracker import TrackerWidget
from gui.animal_tracker import AnimalTrackerWidget
from gui.body_tracker import BodyTrackerWidget
from gui.eye_tracker import EyesTrackerWidget
from gui.tail_tracker import TailTrackerWidget
from gui.gui import ZebraTrackGUI

# get base folder location on different computers
DATA_LOCATION = {
    'hplaptop': '/home/martin/Downloads/Escapes/',
    'O1-619': '/home/martin/Documents/Escapes/',
    'L-O1-620': '/home/martinprivat/ownCloud/Escapes/',
    'TheUgly': ''
}
host = socket.gethostname()
BASEFOLDER = DATA_LOCATION[host]

# relative path
FISHDATA = os.path.join(BASEFOLDER, 'fish.csv')
SELECT = [25]
DISPLAY = True

fish_data = pd.read_csv(
    FISHDATA, 
    usecols=['fish','video_file','timestamp_file','fov_size_mm']
)

for _, experiment in fish_data.iloc[SELECT,:].iterrows():
    fish = experiment['fish'] 
    video_file = os.path.join(BASEFOLDER, experiment['video_file']) 
    timestamp_file = os.path.join(BASEFOLDER, experiment['timestamp_file']) 
    fov_size_mm = experiment['fov_size_mm'] 
    print(f'Processing {fish}...')

    # video reader    
    reader = OpenCV_VideoReader()
    reader.open_file(video_file, safe=False, crop=(0,0,1200,600))
    #reader.open_file(video_file, safe=False)
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    background = StaticBackground(
        video_reader=reader
    )

    #assignment = LinearSumAssignment(distance_threshold=50)
    LUT = np.hstack(( np.zeros((600,600)) , np.ones((600,600)) ))
    #X,Y = np.meshgrid(np.arange(1800) // 600,np.arange(1800) // 600)
    #LUT = X + 3*Y

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

    window = ZebraTrackGUI(
        reader, 
        background, 
        [fish_tracker, paramecia_tracker]
    )
    sys.exit(app.exec())