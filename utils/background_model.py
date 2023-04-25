import cv2
import numpy as np
from numpy.typing import NDArray
from scipy import stats
from typing import Protocol, Tuple

class VideoReader(Protocol):
    def next_frame(self) -> Tuple[bool,NDArray]:
        """return the next frame in the movie, 
        and a boolean if the operation succeeded"""

    def number_of_frames(self) -> int:
        """return number of frames in the movie"""

def select_k_sample_frames(video_reader: VideoReader, k=500):
    pass

def background_model_mode(sample_frames):
    """
    Take sample images from the video and return the mode for each pixel
    Input:
        sample_frames: m x n x k numpy.float32 array where k is the number of 
        frames
    Output:
        background: m x n numpy.float32 array
    """
    return stats.mode(sample_frames,axis=2)