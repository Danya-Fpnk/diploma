import cv2
import numpy as np
from display import model, class_names
import cvzone
import math
import yaml


def load_video_areas(file_path):
    video_areas = {}

    with open(file_path, 'r') as file:
        areas = yaml.safe_load(file)

    for video, data in areas['videos'].items():  # Iterate over key-value pairs
        video_areas[f'video/{video}.mp4'] = {}
        video_areas[f'video/{video}.mp4']['waiting_area'] = data['waiting_areas']  # Access 'waiting_areas' from the dictionary 'data'

    print(video_areas)
    return video_areas


video_areas = load_video_areas('config_video_areas.yml')


class VideoCapture:
    def __init__(self, video_source=0, speed=9):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.waiting_area = np.array(video_areas[video_source]['waiting_area'], np.int32)
        print(self.waiting_area, self.waiting_area.shape, self.waiting_area)

        self.last_frame = None
        self.speed = speed
        self.frame_count = 0
        self.prev_boxes = []

    def calculate_distance(self, box1, box2):
        center1 = ((box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2)
        center2 = ((box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2)
        return (center1[0] - center2[0]) + (center1[1] - center2[1])

    def get_frame(self, top_left_x = 100, top_left_y = 100, bottom_right_x = 1600, bottom_right_y = 1600):
        while True:
            objects_cnt = 0
            inside_counts = 0
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                self.frame_count += 1
                if not self.frame_count % self.speed == 0:
                    continue

                if ret is True:
                    self.last_frame = frame.copy()
                else:
                    frame = self.last_frame.copy()

                results = model(frame, stream=True, classes=[0, 2])

                current_boxes = []
                for r in results:
                    for box in r.boxes:
                        objects_cnt += 1

                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                        conf = math.ceil((box.conf[0] * 100)) / 100
                        cls = int(box.cls[0])

                        is_waiting = False
                        if self.prev_boxes:
                            distances = [self.calculate_distance((x1, y1, x2, y2), prev) for prev in self.prev_boxes]
                            if min(distances) < 2:
                                is_waiting = True

                        cvzone.putTextRect(frame, f'is_waiting: {is_waiting}', (max(0, x1), max(35, y1)), scale=1,
                                           thickness=1)

                        current_boxes.append((x1, y1, x2, y2))

                        cx, cy = x2 // 2, y2 // 2
                        counts = cv2.pointPolygonTest(self.waiting_area, pt=(cx, cy), measureDist=False)
                        if inside_counts == 1:  # Inside the defined region
                            inside_counts += 1

                print(inside_counts)
                self.prev_boxes = current_boxes.copy()

                cv2.polylines(frame, [self.waiting_area], True, (0, 0, 255), 6)

                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), objects_cnt

    def set_vid(self, video_source=0):
        self.__del__()
        self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source
        self.waiting_area = np.array(video_areas[video_source]['waiting_area'], np.int32)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
