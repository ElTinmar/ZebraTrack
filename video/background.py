import numpy as np
from numpy.typing import NDArray
from scipy import stats
from typing import Protocol, Tuple
from imconv import im2gray, im2single
    
class VideoReader(Protocol):
    def next_frame(self) -> Tuple[bool,NDArray]:
        """return the next frame in the movie, 
        and a boolean if the operation succeeded"""

    def get_number_of_frame(self) -> int:
        """return number of frames in the movie"""

    def seek_to(self, index) -> None:
        """go to a specific frame retrieveable with a call to next_frame"""

    def get_width(self) -> int:
        """return width"""
    
    def get_height(self) -> int:
        """return height"""

    def get_num_channels(self) -> int:
        """return number of channels"""

    def get_type(self) -> np.dtype:
        """return data type"""

class StaticBackground:
    def __init__(
            self,
            video_reader: VideoReader, 
            num_sample_frames: int = 500
        ) -> None:
        self.video_reader = video_reader
        self.num_sample_frames = num_sample_frames
        self.background = None

    def sample_frames_evenly(self) -> NDArray:
        '''
        Sample frames evenly from the whole video
        '''
        height = self.video_reader.get_height()
        width = self.video_reader.get_width()
        numframes = self.video_reader.get_number_of_frame()
        sample_indices = np.linspace(0, numframes-1, self.num_sample_frames, dtype = np.int64)
        sample_frames = np.empty((height, width, self.num_sample_frames), dtype=np.float32)
        for i,index in enumerate(sample_indices):
            self.video_reader.seek_to(index)
            rval, frame = self.video_reader.next_frame()
            if rval:
                sample_frames[:,:,i] = im2single(im2gray(frame))
            else:
                RuntimeError('StaticBackground::sample_frames_evenly frame not valid')
        return sample_frames

    def compute_background(self, frame_collection: NDArray) -> None:
        """
        Take sample images from the video and return the mode for each pixel
        Input:
            sample_frames: m x n x k numpy.float32 array where k is the number of 
            frames
        Output:
            background: m x n numpy.float32 array
        """
        self.background = stats.mode(frame_collection, axis=2, keepdims=False).mode

    def initialize_background_model(self):
        frame_collection = self.sample_frames_evenly()
        self.compute_background(frame_collection)

    def subtract_background(self, image: NDArray) -> NDArray:
        return image - self.background 

class DynamicBackground:
    def __init__(self) -> None:
        pass

    def update_policy(self) -> bool:
        '''
        returns True if next image should be added to the background model, 
        returns False otherwise 
        '''
        pass

    def update_background(self, image: NDArray) -> NDArray:
        pass

    def subtract_background(self, image: NDArray) -> NDArray: 
        pass
        
