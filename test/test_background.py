from utils.video_reader import OpenCV_VideoReader
import utils.background_model as bckg
import cv2
from utils.im2float import im2single
from utils.im2gray import im2gray

mov = OpenCV_VideoReader('toy_data/Rajan_et_al_2022.mp4',safe=False)
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
    bckg_sub = (im2single(im2gray(frame)) - background)**2
    bckg_sub_norm = (bckg_sub - bckg_sub.min()) / (bckg_sub.max() - bckg_sub.min())
    cv2.imshow('Background Subtraction', bckg_sub_norm)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    
cv2.destroyAllWindows()


