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
        video_areas[f'video/{video}.mp4'] = data

    print(video_areas)
    return video_areas


video_areas = load_video_areas('config_video_areas.yml')


class VideoCapture:
    def __init__(self, video_source, tracked_objects, speed=9):
        self.video_source = video_source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.video_areas = { key: np.array(value, np.int32) for key, value in video_areas[video_source].items() }
        print(self.video_areas)
        print('self.video_areas')

        self.last_frame = None
        self.speed = speed
        self.frame_count = 0
        self.prev_boxes = []
        self.tracked_objects = [class_names.index(tracked_object) for tracked_object in tracked_objects]

    def calculate_distance(self, box1, box2):
        center1 = ((box1[0] + box1[2]) / 2, (box1[1] + box1[3]) / 2)
        center2 = ((box2[0] + box2[2]) / 2, (box2[1] + box2[3]) / 2)
        return (center1[0] - center2[0]) + (center1[1] - center2[1])

    def dilate_polygon(self, polygon, dilation_size):
        # Создаем структурирующий элемент для дилатации
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilation_size, dilation_size))
        # Применяем дилатацию к маске полигона
        dilated_polygon = cv2.dilate(polygon, kernel, iterations=1)
        return dilated_polygon

    def get_frame(self):
        dilation_size = 40  # Размер расширения полигонов
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

                # Создаем маску для всех полигонов с дилатацией
                mask = np.zeros_like(frame)
                for area_key in self.video_areas.keys():
                    polygon = np.array(self.video_areas[area_key], dtype=np.int32)
                    dilated_mask = np.zeros_like(frame)
                    cv2.fillPoly(dilated_mask, [polygon], (255,) * frame.shape[2])
                    dilated_polygon = self.dilate_polygon(dilated_mask, dilation_size)
                    mask = cv2.bitwise_or(mask, dilated_polygon)

                # Применяем маску для вырезания всех полигонов сразу
                masked_frame = cv2.bitwise_and(frame, mask)

                # Анализируем masked_frame с помощью YOLO
                results = model(masked_frame, stream=True, classes=self.tracked_objects)

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

                        # Теперь проверяем, находится ли центр в одной из маскированных областей
                        for area_key in self.video_areas.keys():
                            polygon = np.array(self.video_areas[area_key], dtype=np.int32)
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            if cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0:
                                inside_counts += 1

                print(inside_counts)
                self.prev_boxes = current_boxes.copy()

                # Отрисовываем полигоны
                for area_key in self.video_areas.keys():
                    polygon = np.array(self.video_areas[area_key], dtype=np.int32)
                    if area_key == 'waiting_straight_area':
                        cv2.polylines(frame, [polygon], True, (0, 0, 255), 6)
                    elif area_key == 'waiting_left_area':
                        cv2.polylines(frame, [polygon], True, (0, 255, 0), 6)
                    else:
                        cv2.polylines(frame, [polygon], True, (0, 255, 255), 6)

                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), objects_cnt


    def set_vid(self, video_source=0):
        self.__del__()
        self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source

        self.video_areas = { key: np.array(value, np.int32) for key, value in video_areas[video_source].items() }
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
