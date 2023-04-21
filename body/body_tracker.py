from typing import Tuple 
import numpy as np
from numpy.typing import NDArray

def body_tracker(frame) -> Tuple(NDArray,NDArray):
    """
    Track the centroid and anteroposterior axis for a single fish
    Input: 
        frame: single precision, grayscale image as numpy array
    Output:
        (centroid, headind_direction): centroid and heading direction
            of the fish
    """

    pass