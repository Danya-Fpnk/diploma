import cv2
from display import model, class_names
import cvzone
import math


class VideoCapture:
    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.last_frame = None

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret is True:
                results = model(frame, stream=True)
                self.last_frame = frame
            else:
                results = model(self.last_frame, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(self.last_frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])
                    cvzone.putTextRect(self.last_frame, f'{class_names[cls]}  {conf} ', (max(0, x1), max(35, y1)), scale=1,
                                       thickness=1)
            return cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)

    def set_vid(self, video_source=0):
        self.__del__()
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
