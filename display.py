from ultralytics import YOLO
# import cv2
# import cvzone
# import math
#
model = YOLO("../YOLO_WEIGHTS/yolov8n.pt")
class_names = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis",
    "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon",
    "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog",
    "pizza", "donut", "cake", "chair", "couch", "potted plant", "bed", "dining table",
    "toilet", "tv", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
    "teddy bear", "hair drier", "toothbrush"
]
#
#
# cap = cv2.VideoCapture(0)
# cap.set(3, 1280)
# cap.set(4, 720)
#
# while True:
#     success, img = cap.read()
#     results = model(img, stream=True)
#     for r in results:
#         boxes = r.boxes
#         for box in boxes:
#             x1, y1, x2, y2 = box.xyxy[0]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#             print(x1, y1, x2, y2)
#             cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
#
#             conf = math.ceil((box.conf[0]*100))/100
#             cls = int(box.cls[0]) #converting the float to int so that the class name can be called
#             cvzone.putTextRect(img,f'{class_names[cls]}  {conf} ',(max(0,x1),max(35,y1)),scale=1,thickness=1)
#
#             cv2.imshow("Image", img)
#             cv2.waitKey(1)
#
# if __name__ =="__main__" :
#     main()