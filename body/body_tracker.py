from typing import Tuple 
import numpy as np
from numpy.typing import NDArray
import cv2
from sklearn.decomposition import PCA
from utils.conncomp_filter import bwareaopen


def body_tracker(frame, method) -> Tuple[NDArray,NDArray]:
    """
    Track the centroid and anteroposterior axis for a single fish
    Input: 
        frame: single precision, grayscale image as numpy array
    Output:
        (centroid, headind_direction): centroid and heading direction
            of the fish
    """

    # Threshold image to get only the fish 
    # Get result

    pass

def body_tracker_PCA(
        frame: NDArray, 
        threshold_intensity: float, 
        threshold_area: int
        ) -> Tuple[NDArray,NDArray,NDArray]:
    """
    Frame should be single or double precision with values between 0 and 1.
    """

    # threshold and remove small objects 
    fish_mask = bwareaopen(frame >= threshold_intensity, min_size=threshold_area)
    blob_coordinates = np.argwhere(fish_mask)

    if blob_coordinates.size == 0:
        # nothing was detected above threshold
        return (None, None, None)
    else:
        # match x,y and image coordinates
        blob_coordinates = blob_coordinates[:,[1, 0]]

        # PCA
        pca = PCA()
        scores = pca.fit_transform(blob_coordinates)
        components = pca.components_.T
        heading = components[:,0]
        centroid = pca.mean_

        # correct orientation
        if abs(max(scores[:,0])) > abs(min(scores[:,0])):
            heading = -heading

        return (centroid, heading, fish_mask)
      

def body_tracker_moments(frame: NDArray) -> Tuple[NDArray,NDArray]:
    pass
