import tkinter
import PIL.Image, PIL.ImageTk

from traffic_light import TrafficLight
from video_utils import VideoCapture


class App:
    def __init__(self, window, window_title, video_sources=['arrived_car.mp4', 'waiting_people.mp4']):
        self.window = window
        self.window.title(window_title)

        self.canvas_width = 250
        self.canvas_height = 325
        self.vids = {
            'left_car': VideoCapture(video_sources[0]),
            'people': VideoCapture(video_sources[1]),
            'right_car': VideoCapture(video_sources[0])
        }

        self.places = {
            'left_car': [10, self.canvas_height+10],
            'people': [self.canvas_width+10, 10],
            'right_car': [self.canvas_width*2+10, self.canvas_height+10]
        }

        self.canvases = {}
        self.change_video_button = tkinter.Button(window, text="Change Left Car Video", command=self.change_left_car_video)
        self.change_video_button.place(x=10, y=700)

        for key in self.vids.keys():
            canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
            canvas.place(
                x=self.places[key][0],
                y=self.places[key][1],
                width=self.canvas_width,
                height=self.canvas_height
            )
            self.canvases[key] = canvas

        TrafficLight(self.window)

        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        self.photos = []
        for key in self.vids.keys():
            # Get a frame from the video source
            frame = self.vids[key].get_frame()

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(image=resized_image)
            self.canvases[key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos.append(photo)

        self.window.after(self.delay, self.update)

    def change_left_car_video(self):
        # Вызов set_vid для изменения видео на 'walking_people.mp4'
        self.vids['left_car'].set_vid('walking_people.mp4')

if __name__ == "__main__":
    # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV")
