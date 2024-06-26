from video_tools import Buffered_OpenCV_VideoReader, OpenCV_VideoReader, StaticBackground, InpaintBackground, Polarity, VideoDisplay, FFMPEG_VideoWriter_GPU
from image_tools import im2single, im2gray
from tracker import (
    GridAssignment, MultiFishTracker_CPU, MultiFishOverlay_opencv, MultiFishTracking,
    AnimalTracker_CPU, AnimalOverlay_opencv, AnimalTrackerParamTracking, AnimalTrackerParamOverlay,
    BodyTracker_CPU, BodyOverlay_opencv, BodyTrackerParamTracking, BodyTrackerParamOverlay,
    EyesTracker_CPU, EyesOverlay_opencv, EyesTrackerParamTracking, EyesTrackerParamOverlay,
    TailTracker_CPU, TailOverlay_opencv, TailTrackerParamTracking, TailTrackerParamOverlay
)
from geometry import Affine2DTransform
from tqdm import tqdm
import numpy as np
import multiprocessing as mp

mp.set_start_method('spawn')

INPUT_VIDEO = 'toy_data/freely_swimming_param.avi'
#INPUT_VIDEO = 'toy_data/head_embedded_param.avi'
EXPORT_FPS = 100

# display
q = mp.Queue()
q_eyes = mp.Queue()
q_tail = mp.Queue()
display = VideoDisplay(q, fps=10, winname='tracking')
display_eyes = VideoDisplay(q_eyes, fps=10, winname='eyes')
display_tail = VideoDisplay(q_tail, fps=10, winname='tail')
display.start()
display_eyes.start()
display_tail.start()

# compute background
background_reader = OpenCV_VideoReader()
background_reader.open_file(INPUT_VIDEO)

background = StaticBackground(
    num_sample_frames = 100,
    video_reader = background_reader,
    polarity = Polarity.DARK_ON_BRIGHT,
)
background.initialize()

# buffered video reader
video_reader = Buffered_OpenCV_VideoReader()
video_reader.open_file(INPUT_VIDEO)
#video_reader.start()

height = video_reader.get_height()
width = video_reader.get_width()
fps = video_reader.get_fps()  
num_frames = video_reader.get_number_of_frame()

# Fish ID Assignment
LUT = np.zeros((height, width))
assignment = GridAssignment(LUT)

# Data accumulator
accumulator = None

# tracking 
animal_tracker = AnimalTracker_CPU(
    assignment=assignment, 
    tracking_param=AnimalTrackerParamTracking(
        pix_per_mm=40,
        target_pix_per_mm=5,
        animal_intensity=0.07,
        animal_brightness=0.0,
        animal_gamma=1.0,
        animal_contrast=1.0,
        min_animal_size_mm=1.0,
        max_animal_size_mm=30.0,
        min_animal_length_mm=0,
        max_animal_length_mm=0,
        min_animal_width_mm=0,
        max_animal_width_mm=0,
        blur_sz_mm=1/5,
        median_filter_sz_mm=0,
    )
)
body_tracker = BodyTracker_CPU(
    tracking_param=BodyTrackerParamTracking(
        pix_per_mm=40,
        target_pix_per_mm=10,
        body_intensity=0.1,
        body_brightness=0.0,
        body_gamma=1.0,
        body_contrast=3.0,
        min_body_size_mm=3.0,
        max_body_size_mm=30.0,
        min_body_length_mm=0,
        max_body_length_mm=0,
        min_body_width_mm=0,
        max_body_width_mm=0,
        crop_dimension_mm=(5.5,5.5),
        blur_sz_mm=1/7.5,
        median_filter_sz_mm=0,
    )
)
eyes_tracker = EyesTracker_CPU(
    tracking_param=EyesTrackerParamTracking(
        pix_per_mm=40,
        target_pix_per_mm=40,
        eye_brightness=0.0,
        eye_gamma=3.0,
        eye_thresh_lo=0.3,
        eye_thresh_hi=0.7,
        eye_dyntresh_res=5,
        eye_contrast=5.0,
        eye_size_lo_mm=0.8,
        eye_size_hi_mm=10.0,
        blur_sz_mm=0.06,
        median_filter_sz_mm=0,
        crop_dimension_mm=(1.0,1.5),
        crop_offset_mm=-0.75
    )
)
tail_tracker = TailTracker_CPU(
    tracking_param=TailTrackerParamTracking(
        pix_per_mm=40,
        target_pix_per_mm=20,
        ball_radius_mm=0.05,
        arc_angle_deg=90,
        n_tail_points=6,
        n_pts_arc=20,
        n_pts_interp=40,
        tail_length_mm=2.4,
        dist_swim_bladder_mm=0.0,
        blur_sz_mm=0.06,
        median_filter_sz_mm=0,
        tail_brightness=0.0,
        tail_contrast=3.0,
        tail_gamma=0.75,
        crop_dimension_mm=(3.5,3.5),
        crop_offset_tail_mm=1.75
    )
)

tracker = MultiFishTracker_CPU(
    max_num_animals=1,            
    accumulator=accumulator,
    animal=animal_tracker,
    body=body_tracker, 
    eyes=eyes_tracker, 
    tail=tail_tracker
)

# overlay
animal_overlay = AnimalOverlay_opencv(AnimalTrackerParamOverlay())
body_overlay = BodyOverlay_opencv(BodyTrackerParamOverlay())
eyes_overlay = EyesOverlay_opencv(EyesTrackerParamOverlay())
tail_overlay = TailOverlay_opencv(TailTrackerParamOverlay())

overlay = MultiFishOverlay_opencv(
    animal_overlay,
    body_overlay,
    eyes_overlay,
    tail_overlay
)

# Video exporters
video_writer = FFMPEG_VideoWriter_GPU(
    height=height,
    width=width,
    fps=EXPORT_FPS,
    filename='freely_swimming_param_tracking.avi',
    codec = 'libx264',
    preset = 'medium'
)

video_writer_eyes= FFMPEG_VideoWriter_GPU(
    height=eyes_tracker.tracking_param.crop_dimension_px[1],
    width=eyes_tracker.tracking_param.crop_dimension_px[0],
    fps=EXPORT_FPS,
    filename='freely_swimming_param_eyes_tracking.avi',
    codec = 'libx264',
    preset = 'medium'
)

video_writer_tail = FFMPEG_VideoWriter_GPU(
    height=tail_tracker.tracking_param.crop_dimension_px[1],
    width=tail_tracker.tracking_param.crop_dimension_px[0],
    fps=EXPORT_FPS,
    filename='freely_swimming_param_tail_tracking.avi',
    codec = 'libx264',
    preset = 'medium'
)


try:
    for i in tqdm(range(num_frames)):
        (rval, frame) = video_reader.next_frame()
        if not rval:
            raise RuntimeError('VideoReader was unable to read the whole video')
        
        # convert
        frame_gray = im2single(im2gray(frame))

        # background subtraction
        image_sub = background.subtract_background(frame_gray)

        # track
        tracking = tracker.track(image_sub)

        # display tracking
        oly = overlay.overlay(frame_gray, tracking)
        display.queue_image(oly)

        # save video
        if oly is not None:
            video_writer.write_frame(oly[:,:,[2,1,0]])
        else:
            video_writer.write_frame(np.zeros((height,width), dtype=np.uint8))
        
        # display eyes 
        if tracking.eyes is not None and tracking.eyes[0] is not None:
            s = eyes_tracker.tracking_param.resize
            tx, ty = -tracking.eyes[0].origin
            S = Affine2DTransform.scaling(s,s)
            T = Affine2DTransform.translation(tx, ty)
            eye_oly = eyes_overlay.overlay(tracking.eyes[0].image, tracking.eyes[0], T @ S)
            display_eyes.queue_image(eye_oly)
            video_writer_eyes.write_frame(eye_oly[:,:,[2,1,0]])
        else:
            video_writer_eyes.write_frame(np.zeros((eyes_tracker.tracking_param.crop_dimension_px[1],eyes_tracker.tracking_param.crop_dimension_px[0],3), dtype=np.uint8))

        # display tail
        if tracking.tail is not None and tracking.tail[0] is not None:
            s = tail_tracker.tracking_param.resize
            tx, ty = -tracking.tail[0].origin
            S = Affine2DTransform.scaling(s,s)
            T = Affine2DTransform.translation(tx, ty)
            tail_oly = tail_overlay.overlay(tracking.tail[0].image, tracking.tail[0], T @ S)
            display_tail.queue_image(tail_oly)
            video_writer_tail.write_frame(tail_oly[:,:,[2,1,0]])
        else:
            video_writer_tail.write_frame(np.zeros((tail_tracker.tracking_param.crop_dimension_px[1],tail_tracker.tracking_param.crop_dimension_px[0],3), dtype=np.uint8))

finally:
    video_reader.exit()
    video_reader.join()
    display.exit()
    display_eyes.exit()
    display_tail.exit()
    display.join()
    display_eyes.join()
    display_tail.join()

video_writer.close()
video_writer_eyes.close()
video_writer_tail.close()


