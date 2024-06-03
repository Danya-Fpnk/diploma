import time

import cv2
import numpy as np
from ultralytics import YOLO

from model import class_names

from video_utils import get_masked_frame


class RealTimeVideoCapture:
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
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, frame)
            else:
                return (ret, None)
        else:
            return (False, None)

    def analyze_frame(self, masked_frame, frame):
        results = self.model.track(masked_frame, classes=self.tracked_classes, imgsz=640, show=False, persist=True)

        detect_unixtime = int(time.time())
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu()
            clss = results[0].boxes.cls.cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()

            for box, track_id, cls in zip(boxes, track_ids, clss):

                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                for area_key in self.video_areas.keys():
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

    def analyze_objects(self):
        ret, frame = self.last_frame

        masked_frame, self.mask = get_masked_frame(
            self.mask,
            frame,
            self.dilation_size,
            self.video_areas
        )

        frame = self.analyze_frame(masked_frame, frame)

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
