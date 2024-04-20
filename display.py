from ultralytics import YOLO
# import cv2
# import cvzone
# import math
#
model = YOLO("../YOLO_WEIGHTS/yolov8n.pt")
model.classes = [0, 2]
class_names = {0: "person", 2: "car"}