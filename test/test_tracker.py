import os
import pandas as pd
import cv2
from video.video_reader import OpenCV_VideoReader
from video.background import StaticBackground, DynamicBackground, DynamicBackgroundMP
from trackers.animal import AnimalTracker, AnimalTrackerParamTracking, AnimalTrackerParamOverlay
from trackers.body import BodyTracker, BodyTrackerParamTracking, BodyTrackerParamOverlay
from trackers.eyes import EyesTracker, EyesTrackerParamTracking, EyesTrackerParamOverlay
from trackers.tail import TailTracker, TailTrackerParamTracking, TailTrackerParamOverlay
from trackers.tracker import Tracker
from trackers.assignment import LinearSumAssignment
from helper.imconvert import im2gray, im2single

BASEFOLDER = '/home/martin/Documents/Escapes/'
FISHDATA = os.path.join(BASEFOLDER, 'fish.csv')
SELECT = [25]

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
    reader.open_file(video_file, safe=False)
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    background = DynamicBackgroundMP(
        height=height,
        width=width,
        num_images = 500,
        every_n_image = 200
    )

    # tracking 
    animal_tracker = AnimalTracker(
        AnimalTrackerParamTracking(),
        AnimalTrackerParamOverlay()
    )
    body_tracker = BodyTracker(
        BodyTrackerParamTracking(),
        BodyTrackerParamOverlay()
    )
    eyes_tracker = EyesTracker(
        EyesTrackerParamTracking(),
        EyesTrackerParamOverlay()
    )
    tail_tracker = TailTracker(
        TailTrackerParamTracking(),
        TailTrackerParamOverlay()
    )
    assignment = LinearSumAssignment(distance_threshold=50)
    accumulator = None
    tracker = Tracker(            
        assignment,
        accumulator,
        animal_tracker,
        body_tracker, 
        eyes_tracker, 
        tail_tracker
    )

    cv2.namedWindow('tracking')
    while True:
        ret, image = reader.next_frame()
        if not ret:
            break

        img = im2single(im2gray(image))
        image_sub = background.subtract_background(img)
        tracking = tracker.track(image_sub)
        overlay = tracker.overlay(image, tracking)
        if overlay is not None:res = {
                'identities': None, 
                'animals': None,
                'body': None,
                'eyes': None,
                'tail': None
            }
            cv2.imshow('tracking', overlay)
            cv2.waitKey(1)
