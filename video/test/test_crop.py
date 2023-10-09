from video.video_reader import OpenCV_VideoReader
from video.video_writer import OpenCV_VideoWriter
from video.video_display import VideoDisplay 
from tqdm import tqdm

video_file = "/home/martin/ownCloud - martin.privat@bi.mpg.de@owncloud.gwdg.de/Escapes/data/2023_09_14_08.avi"

# open reader
reader = OpenCV_VideoReader()
reader.open_file(video_file, safe=False, crop=(0,0,600,600))
num_frames = reader.get_number_of_frame()

# open writer
writer = OpenCV_VideoWriter( 
    height = 600, 
    width = 600, 
    fps = 200, 
    filename = 'single_larva.avi'
)

display = VideoDisplay(fps=10)
display.start()

try:
    for i in tqdm(range(num_frames)):
        ret, image = reader.next_frame()
        if not ret:
            break
        display.queue_image(image)
        writer.write_frame(image)
finally:
    writer.close()
    display.exit()
    display.join()