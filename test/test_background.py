from utils.video_reader import OpenCV_VideoReader
import utils.background_model as bckg
import cv2
from utils.im2float import im2single
from utils.im2gray import im2gray
from utils.imadjust import imadjust
from skimage.morphology import area_opening
from skimage.measure import regionprops, moments
from scipy.ndimage import median_filter

mov = OpenCV_VideoReader('toy_data/behavior_2000.avi',safe=False)
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
    fish = area_opening(bckg_sub_norm, area_threshold=200)
    cv2.imshow('Background Subtraction', fish)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows()


