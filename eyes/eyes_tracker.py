from typing import Tuple 
import numpy as np
from numpy.typing import NDArray
import cv2

def eyes_tracker(
        frame: NDArray,
        threshold_eye_intensity: float,
        threshold_eye_area: int,
        ) -> Tuple[float, float]:
    """
    Track the left and right eyes for a single fish
    Input: 
        frame: single precision, grayscale image as numpy array
    Output:
        (left,right): angle in radians for the left and right eye
        with respect to the anteroposterior axis 
    """
    
    pass