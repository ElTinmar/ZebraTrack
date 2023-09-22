import os
import pandas as pd
from video.video_reader import OpenCV_VideoReader
from video.background import StaticBackground, DynamicBackground, DynamicBackgroundMP

BASEFOLDER = '/home/martin/Documents/Escapes/'
FISHDATA = os.path.join(BASEFOLDER, 'fish.csv')
SELECT = [25]

fish_data = pd.read_csv(
    FISHDATA, 
    usecols=['fish','video_file','timestamp_file','fov_size_mm']
)

for _, experiment in fish_data.iloc[SELECT,:].iterrows():
    fish = experiment['fish'] 
    video_file = os.path.join(BASEFOLDER, experiment['video_file']) 
    timestamp_file = os.path.join(BASEFOLDER, experiment['timestamp_file']) 
    fov_size_mm = experiment['fov_size_mm'] 
    print(f'Processing {fish}...')

    # video reader
    reader = OpenCV_VideoReader()
    reader.open_file(video_file, safe=True)
    num_frames = reader.get_number_of_frame()
    height = reader.get_height()
    width = reader.get_width()

    # background subtraction
    background = DynamicBackgroundMP(
        height=height,
        width=width,
        num_images = 500,
        every_n_image = 200
    )

    # tracking 