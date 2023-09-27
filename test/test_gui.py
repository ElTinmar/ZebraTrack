import os
import socket
import pandas as pd
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication

from video.video_reader import OpenCV_VideoReader
from video.background import StaticBackground, DynamicBackground, DynamicBackgroundMP
from trackers.assignment import LinearSumAssignment, GridAssignment
from widgets.tracker import TrackerWidget
from widgets.animal_tracker import AnimalTrackerWidget
from widgets.body_tracker import BodyTrackerWidget
from widgets.eye_tracker import EyesTrackerWidget
from widgets.tail_tracker import TailTrackerWidget
from gui import ZebraTrackGUI

host = socket.gethostname()
BASEFOLDER = '/home/martin/ownCloud - martin.privat@bi.mpg.de@owncloud.gwdg.de/Escapes/'
if host == 'hplaptop':
    BASEFOLDER = '/home/martin/Downloads/Escapes/'
if host == 'O1-619':
    BASEFOLDER = '/home/martin/Documents/Escapes/'
if host == 'L-O1-620':
    BASEFOLDER = '/home/martinprivat/ownCloud/Escapes/'
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
    reader.open_file(video_file, safe=False, crop=(0,0,600,600))
    #reader.open_file(video_file, safe=False)
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    background = StaticBackground(
        video_reader=reader
    )

    #assignment = LinearSumAssignment(distance_threshold=50)
    LUT = np.zeros((600,600))
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