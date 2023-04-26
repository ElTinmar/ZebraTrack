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

mov = OpenCV_VideoReader('toy_data/behavior_2000.avi',safe=False)

# Background model
sample = bckg.sample_frames_evenly(mov,500)
background = bckg.background_model_mode(sample)

# plot background
cv2.imshow('Background',background)
cv2.waitKey(1)
cv2.destroyAllWindows()

# background substraction
mov.reset_reader()
while True:
    rval, frame = mov.next_frame()
    if not rval:
        break
    bckg_sub = abs(im2single(im2gray(frame)) - background)
    bckg_sub_norm = imadjust(bckg_sub,bckg_sub.min(),bckg_sub.max(),0,1)
    #bckg_sub_norm_filt = median_filter(bckg_sub_norm,size=(5,5))

    # this is very good but slow
    #fish = area_opening(bckg_sub_norm, area_threshold=est_fish_area_pixel)
    cv2.imshow('Background Subtraction', bckg_sub_norm)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows()

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

alpha = 100
threshold_intensity = 0.1
threshold_area = est_fish_area_pixel
mov.reset_reader()
while True:
    rval, frame = mov.next_frame()
    if not rval:
        break
    bckg_sub = abs(im2single(im2gray(frame)) - background)
    centroid, heading, _ = body_tracker_PCA(bckg_sub, threshold_intensity, threshold_area)
    if centroid is not None:
        pt1 = centroid
        pt2 = centroid + alpha*heading
        tracking = cv2.line(
            frame,
            pt1.astype(np.int32),
            pt2.astype(np.int32),
            (0,0,255)
        )
        cv2.imshow('Tracking', tracking)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    
cv2.destroyAllWindows()

# Paramecia tracking
from utils.conncomp_filter import bwareafilter

alpha = 100
threshold_intensity = 0.1
threshold_intensity_param = 0.025
threshold_area = est_fish_area_pixel
threshold_area_param_min = 15
threshold_area_param_max = est_fish_area_pixel

mov.reset_reader()
while True:
    rval, frame = mov.next_frame()
    if not rval:
        break
    bckg_sub = abs(im2single(im2gray(frame)) - background)
    centroid, heading, _ = body_tracker_PCA(bckg_sub, threshold_intensity, threshold_area)
    param_mask = bwareafilter(
        bckg_sub >= threshold_intensity_param, 
        min_size=threshold_area_param_min, 
        max_size=threshold_area_param_max
    )
    tracking = frame
    tracking[:,:,2] =  255*param_mask
    if centroid is not None:
        pt1 = centroid
        pt2 = centroid + alpha*heading
        tracking = cv2.line(
            tracking,
            pt1.astype(np.int32),
            pt2.astype(np.int32),
            (0,0,255)
        )

    cv2.imshow('Tracking', tracking)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows()
