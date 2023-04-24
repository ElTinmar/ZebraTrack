from typing import Tuple 
import numpy as np
from numpy.typing import NDArray
import cv2

def body_tracker(frame, method) -> Tuple(NDArray,NDArray):
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


def body_tracker_PCA(frame) -> Tuple(NDArray,NDArray):
    
    pass

def body_tracker_moments(frame) -> Tuple(NDArray,NDArray):
    pass
