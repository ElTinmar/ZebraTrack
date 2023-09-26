import numpy as np
from video.video_display import VideoDisplay 

display = VideoDisplay(fps=30)
display.start()
for i in range(1000):
    display.queue_image(np.random.randint(0,255,(512,512,3),dtype = np.uint8))
display.exit()
display.join()
