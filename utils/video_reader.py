import cv2

class VideoReader:

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.capture = cv2.VideoCapture(filename)

    def nextFrame(self):
        rval, frame = self.capture.read()
        return frame

    def play(self) -> None:
        cv2.namedWindow(self.filename)
        
        while True:
            cv2.imshow(self.filename,self.nextFrame())
            key = cv2.waitKey(1)
            if key == ord('q'):
                break

        cv2.destroyAllWindows()

    def __del__(self) -> None:
        self.capture.release()