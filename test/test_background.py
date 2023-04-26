from utils.video_reader import OpenCV_VideoReader
import utils.background_model as bckg
import cv2
from utils.im2float import im2single
from utils.im2gray import im2gray
from utils.imadjust import imadjust
from skimage.measure import regionprops, moments
from scipy.ndimage import median_filter
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from math import pi
import numpy as np
from body.body_tracker import body_tracker_PCA
from prey.prey_tracker import prey_tracker
from utils.conncomp_filter import bwareafilter

mov = OpenCV_VideoReader('toy_data/behavior_2000.avi',safe=False)

# Background model
sample = bckg.sample_frames_evenly(mov,500)
background = bckg.background_model_mode(sample)

# estimate the area in pixel of the fish by an ellipse
fish_length_mm = 6
fish_width_mm = 1
pixel_per_mm = 10
mm_per_pixel = 1/pixel_per_mm
est_fish_area_pixel = int(pi * fish_length_mm/2 * fish_width_mm/2 * pixel_per_mm**2)

# estimate threshold (do it once and don't put it in the function ?)
#sorted_pixel_values = bckg_sub_norm.ravel()
#sorted_pixel_values.sort()
#brightest_pixels = sorted_pixel_values[-est_fish_area_pixel:-1]

# Paramecia tracking

alpha = 100
threshold_intensity = 0.1
threshold_area = est_fish_area_pixel

threshold_intensity_eyes = 0.4
threshold_area_eye_min = 100
threshold_area_eye_max = 500

threshold_intensity_param = 0.025
threshold_area_param_min = 15
threshold_area_param_max = est_fish_area_pixel

mov.reset_reader()
while True:
    rval, frame = mov.next_frame()
    if not rval:
        break
    bckg_sub = abs(im2single(im2gray(frame)) - background)
    
    # track fish body
    centroid, component, _ = body_tracker_PCA(
        bckg_sub, 
        threshold_intensity, 
        threshold_area
    )
    heading = component[:,0]
    
    # track paramecia
    prey_centroids, prey_mask = prey_tracker(
        bckg_sub,
        threshold_intensity_param,
        threshold_area_param_min,
        threshold_area_param_max
    )

    # track eyes
    eye_mask = bwareafilter(
        bckg_sub >= threshold_intensity_eyes, 
        min_size=threshold_area_eye_min, 
        max_size=threshold_area_eye_max
    )

    # track tail

    # show tracking
    tracking = frame

    if centroid is not None:
        pt1 = centroid
        pt2 = centroid + alpha*heading
        tracking = cv2.line(
            tracking,
            pt1.astype(np.int32),
            pt2.astype(np.int32),
            (0,0,255)
        )

    for prey_loc in prey_centroids:
        tracking = cv2.circle(tracking,prey_loc.astype(np.int32),10,(0,255,0))

    cv2.imshow('Tracking', tracking)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows()
