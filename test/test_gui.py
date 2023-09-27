import os
import socket
import pandas as pd
import numpy as np
import sys
from video.video_reader import OpenCV_VideoReader
from video.background import StaticBackground, DynamicBackground, DynamicBackgroundMP
from trackers.animal import AnimalTracker, AnimalTrackerParamTracking, AnimalTrackerParamOverlay
from trackers.body import BodyTracker, BodyTrackerParamTracking, BodyTrackerParamOverlay
from trackers.eyes import EyesTracker, EyesTrackerParamTracking, EyesTrackerParamOverlay
from trackers.tail import TailTracker, TailTrackerParamTracking, TailTrackerParamOverlay
from trackers.tracker import Tracker
from trackers.assignment import LinearSumAssignment, GridAssignment
from image.imconvert import im2gray, im2single
from tqdm import tqdm
from PyQt5.QtWidgets import QApplication
from gui import TrackerThreshold

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
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    background = StaticBackground(
        video_reader=reader
    )

    #assignment = LinearSumAssignment(distance_threshold=50)
    LUT = np.zeros((600,600))
    assignment = GridAssignment(LUT)
    accumulator = None

    app = QApplication(sys.argv)
    window = TrackerThreshold(reader, background, assignment)
    sys.exit(app.exec())