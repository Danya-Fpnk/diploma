from ultralytics import YOLO
# import cv2
# import cvzone
# import math
#
model = YOLO("../YOLO_WEIGHTS/yolov8n.pt")
model.classes = [0, 2]
class_names = {0: "person", 2: "car"}
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