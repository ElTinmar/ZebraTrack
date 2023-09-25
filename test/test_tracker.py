import os
import socket
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
from image.imconvert import im2gray, im2single
from tqdm import tqdm

host = socket.gethostname()
BASEFOLDER = '/home/martin/ownCloud - martin.privat@bi.mpg.de@owncloud.gwdg.de/Escapes/'
if host == 'O1-619':
    BASEFOLDER = '/home/martin/Documents/Escapes/'
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
    reader.open_file(video_file, safe=False)
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    
    background = StaticBackground(
        video_reader=reader
    )
    
    '''
    background = DynamicBackgroundMP(
        height=height,
        width=width,
        num_images = 500,
        every_n_image = 200
    )    
    '''

    # tracking 
    animal_tracker = AnimalTracker(
        AnimalTrackerParamTracking(
            pix_per_mm=40,
            target_pix_per_mm=10,
            body_intensity=0.06,
            min_body_size_mm=5.0,
            max_body_size_mm=40.0,
            min_body_length_mm=1.5,
            max_body_length_mm=6.0,
            min_body_width_mm=0.5,
            max_body_width_mm=3.0,
            pad_value_mm=3.0
        ),
        AnimalTrackerParamOverlay()
    )
    body_tracker = BodyTracker(
        BodyTrackerParamTracking(
            pix_per_mm=40,
            target_pix_per_mm=20,
            body_intensity=0.06,
            min_body_size_mm=5.0,
            max_body_size_mm=40.0,
            min_body_length_mm=1.5,
            max_body_length_mm=6.0,
            min_body_width_mm=0.5,
            max_body_width_mm=3.0
        ),
        BodyTrackerParamOverlay()
    )
    eyes_tracker = EyesTracker(
        EyesTrackerParamTracking(
            pix_per_mm=40,
            target_pix_per_mm=40,
            eye_norm=0.2,
            eye_gamma=3.0,
            eye_dyntresh_res=20,
            eye_contrast=1.5,
            eye_size_lo_mm=0.8,
            eye_size_hi_mm=10.0,
            blur_sz_mm=0.06,
            median_filter_sz_mm=0.05,
            dist_eye_midline_mm=0.1,
            crop_dimension_mm=(1.0,1.5),
            crop_offset_mm=1.8
        ),
        EyesTrackerParamOverlay()
    )
    tail_tracker = TailTracker(
        TailTrackerParamTracking(
            pix_per_mm=40,
            target_pix_per_mm=20,
            arc_angle_deg=120,
            n_tail_points=12,
            n_pts_arc=20,
            n_pts_interp=40,
            tail_length_mm=2.3,
            dist_swim_bladder_mm=0.6,
            blur_sz_mm=0.15,
            median_filter_sz_mm=0.15,
            tail_norm=0.15,
            tail_contrast=1.0,
            tail_gamma=0.75,
            crop_dimension_mm=(3.5,3.5),
            crop_offset_tail_mm=2.0
        ),
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

    if DISPLAY:
        cv2.namedWindow('tracking')

    for i in tqdm(range(num_frames)):
        ret, image = reader.next_frame()
        if not ret:
            break

        img = im2single(im2gray(image))
        image_sub = background.subtract_background(img)
        tracking = tracker.track(image_sub)
        if DISPLAY:
            overlay = tracker.overlay(image, tracking)
            if overlay is not None:
                overlay = cv2.resize(overlay,None,None,0.5,0.5)
                cv2.imshow('tracking', overlay)
                cv2.waitKey(1)

    if DISPLAY:
        cv2.destroyAllWindows()