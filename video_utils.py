import cv2
from display import model, class_names
import cvzone
import math


class VideoCapture:
    def __init__(self, video_source=0, width=None, height=None, speed=4):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        if width and height:
            self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.last_frame = None
        self.speed = speed
        self.frame_count = 0

    def get_frame(self):
        while True:
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                self.frame_count += 1
                if not self.frame_count % self.speed == 0:
                    continue
                if ret is True:
                    results = model(frame, stream=True)
                    self.last_frame = frame
                else:
                    results = model(self.last_frame, stream=True)
                    frame = self.last_frame.copy()
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        print(box)
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                        conf = math.ceil((box.conf[0] * 100)) / 100
                        cls = int(box.cls[0])
                        cvzone.putTextRect(frame, f'{class_names[cls]}  {conf} ', (max(0, x1), max(35, y1)), scale=1,
                                           thickness=1)
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def set_vid(self, video_source=0):
        self.__del__()
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
