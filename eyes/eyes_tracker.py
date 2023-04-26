from typing import Tuple 
import numpy as np
from numpy.typing import NDArray
import cv2
from utils.conncomp_filter import bwareafilter
from skimage.measure import label, regionprops

def eyes_tracker(
        frame: NDArray,
        threshold_eye_intensity: float,
        threshold_eye_area_min: int,
        threshold_eye_area_max: int,
        principal_components: NDArray,
        fish_centroid: NDArray
        ) -> Tuple[float, float]:
    """
    Track the left and right eyes for a single fish
    Input: 
        frame: single precision, grayscale image as numpy array
    Output:
        (left,right): angle in radians for the left and right eye
        with respect to the anteroposterior axis 
    """

    eye_mask = bwareafilter(
        frame >= threshold_eye_intensity, 
        min_size = threshold_eye_area_min, 
        max_size = threshold_eye_area_max
    )

    label_img = label(eye_mask)
    regions = regionprops(label_img)

    eye_left = None
    for blob in regions:
        # project coordinates to principal component space
        coord_pc = (blob.centroid - fish_centroid) @ principal_components

