import tkinter
import cv2
import PIL.Image, PIL.ImageTk
from display import model, class_names
import cvzone
import math


class App:
    def __init__(self, window, window_title, video_sources=0):
        self.cn_cnt = 2

        self.window = window
        self.window.title(window_title)
        self.video_sources = video_sources

        self.vid = VideoCapture(video_sources)

        # Create 9 canvases, one for each video source
        self.canvases = []
        for vid in range(self.cn_cnt):
            canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height)
            canvas.pack()
            self.canvases.append(canvas)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        self.photos = []
        for idx in range(self.cn_cnt):
            # Get a frame from the video source
            ret, frame = self.vid.get_frame()

            if ret:
                photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvases[idx].create_image(0, 0, image=photo, anchor=tkinter.NW)
                self.photos.append(photo)

        self.window.after(self.delay, self.update)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        self.vid.set(3, 100)
        self.vid.set(4, 70)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            results = model(frame, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    print(x1, y1, x2, y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

                    conf = math.ceil((box.conf[0] * 100)) / 100
                    cls = int(box.cls[0])
                    cvzone.putTextRect(frame, f'{class_names[cls]}  {conf} ', (max(0, x1), max(35, y1)), scale=1,
                                       thickness=1)
                if ret:
                    # Return a boolean success flag and the current frame converted to BGR
                    return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                else:
                    return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
App(tkinter.Tk(), "Tkinter and OpenCV")