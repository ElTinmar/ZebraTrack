from numpy.typing import NDArray
from scipy import ndimage
import cv2

#TODO should you modify image in place ?
def imcontrast(
        image: NDArray, 
        contrast: float,
        gamma: float,
        intensity_norm: float, 
        blur_size_px: int, 
        medfilt_size_px: int
        ) -> None:
    
    image = cv2.boxFilter(image, -1, (blur_size_px, blur_size_px))
    image[image<0] = 0
    image = image/intensity_norm
    image = ndimage.median_filter(image, size = medfilt_size_px)
    image = contrast*image**gamma
    image[image>1] = 1