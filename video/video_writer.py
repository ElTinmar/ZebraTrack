import cv2
from numpy.typing import NDArray
import numpy as np

# video writer opencv
class OpenCV_VideoWriter:

    def __init__(
            self, 
            height: int, 
            width: int, 
            fps: int = 25, 
            filename: str = 'output.avi',
            fourcc: str = 'XVID'
        ) -> None:
        
        self.height = height
        self.width = width
        self.fps = fps
        self.filename = filename
        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.writer = cv2.VideoWriter(filename, self.fourcc, fps, (height, width))

    def write_frame(self, image: NDArray) -> None:
        # TODO maybe check image dimensions and grayscale
        self.writer.write(image)

    def close(self) -> None:
        self.writer.release()

# video writer ffmpeg
