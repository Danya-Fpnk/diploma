import time
from datetime import datetime
import random

import cv2
import numpy as np
from ultralytics import YOLO

from model import class_names
import yaml

from video_utils import add_mask_to_frame


def load_video_areas(file_path):
    video_areas = {}

    with open(file_path, 'r') as file:
        areas = yaml.safe_load(file)

    for video, data in areas['videos'].items():  # Iterate over key-value pairs
        video_areas[f'video/{video}.mp4'] = data

    return video_areas


video_areas = load_video_areas('config_video_areas.yml')


class VideoCapture:
    def __init__(self, video_source, video_sources, tracked_objects, speed=5):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        self.video_sources = video_sources
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.video_areas = {key: np.array(value, np.int32) for key, value in video_areas[video_source].items()}

        self.last_frame = None
        self.is_last_frame = False
        self.dilation_size = 40
        self.mask = None
        self.speed = speed
        self.frame_count = 0
        self.tracked_classes = [class_names.index(tracked_object) for tracked_object in tracked_objects]

        self.objects_in_areas_stats = {
            'lst_in_waiting_area': {area_key: {tracked_class: {} for tracked_class in self.tracked_classes} for area_key
                                    in self.video_areas.keys()},
            'detect_time': {area_key: {tracked_class: {} for tracked_class in self.tracked_classes} for area_key in
                            self.video_areas.keys()}
        }
        self.model = YOLO("yolov8n.pt")

    def get_frame(self):
        while True:
            if self.vid.isOpened():
                ret, frame = self.vid.read()
                self.is_last_frame = True
                self.frame_count += 1
                if not self.frame_count % self.speed == 0:
                    continue

                if ret is True:
                    self.last_frame = frame.copy()
                    self.is_last_frame = False

            return self.last_frame

    def draw_waiting_areas(self, frame):
        for area_key in self.video_areas.keys():
            polygon = np.array(self.video_areas[area_key], dtype=np.int32)
            if area_key == 'west_east_straight':
                cv2.polylines(frame, [polygon], True, (0, 0, 255), 6)
            elif area_key == 'north_south_straight':
                cv2.polylines(frame, [polygon], True, (0, 255, 0), 6)
            else:
                cv2.polylines(frame, [polygon], True, (0, 255, 255), 6)

        return frame

    def analyze_using_yolo_model(self, masked_frame, frame):
        results = self.model.track(masked_frame, classes=self.tracked_classes, imgsz=640, show=False, persist=True)

        detect_unixtime = int(time.time())
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu()
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, track_id, cls in zip(boxes, track_ids, clss):

                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                for area_key in self.video_areas.keys():
                    polygon = np.array(self.video_areas[area_key], dtype=np.int32)
                    cx = (x1 + x2) // 2
                    if cv2.pointPolygonTest(polygon, (cx, y2), False) >= 0:
                        if track_id in self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls]:
                            self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls][
                                track_id] = detect_unixtime
                        else:
                            # Initialize tracking of new track_id
                            self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls][
                                track_id] = detect_unixtime
                            self.objects_in_areas_stats['detect_time'][area_key][cls][track_id] = detect_unixtime

        for area_key in self.video_areas.keys():
            for cls in self.tracked_classes:
                track_ids = list(self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls].keys())
                for track_id in track_ids:
                    if detect_unixtime - self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls][track_id] > 6:
                        del self.objects_in_areas_stats['lst_in_waiting_area'][area_key][cls][track_id]
                        del self.objects_in_areas_stats['detect_time'][area_key][cls][track_id]

                        # cls_value['lst_in_waiting_area'].pop(track_id, None)
                        # cls_value['detect_time'].pop(track_id, None)
        return frame

    def analyze_frame(self):
        frame = self.last_frame

        masked_frame, self.mask = add_mask_to_frame(
            self.mask,
            frame,
            self.dilation_size,
            self.video_areas
        )

        frame = self.analyze_using_yolo_model(masked_frame, frame)

        frame = self.draw_waiting_areas(frame)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), self.objects_in_areas_stats

    def get_random_video_source(self, video_type):
        if video_type not in self.video_sources:
            raise ValueError(f"Video type '{video_type}' not found in video sources")

        sources = self.video_sources[video_type]
        if isinstance(sources, list):
            selected_source = random.choice(sources)
        else:
            selected_source = sources

        return selected_source

    def set_vid(self, video_source=None, video_type=None):
        if video_source is None:
            video_source = self.get_random_video_source(video_type)
        self.__del__()
        self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source

        self.video_areas = {key: np.array(value, np.int32) for key, value in video_areas[video_source].items()}

        self.objects_in_areas_stats = {
            'lst_in_waiting_area': {area_key: {tracked_class: {} for tracked_class in self.tracked_classes} for area_key
                                    in self.video_areas.keys()},
            'detect_time': {area_key: {tracked_class: {} for tracked_class in self.tracked_classes} for area_key in
                            self.video_areas.keys()}
        }
        if 'pavement' in video_source or 'people' in video_source:
            self.model = YOLO("yolov8n.pt")
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
