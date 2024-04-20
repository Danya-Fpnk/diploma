import tkinter
import PIL.Image, PIL.ImageTk
from datetime import datetime, timedelta
from traffic_light import TrafficLight
from traffic_utils import sum_values_by_key_pattern
from video_utils import VideoCapture


class App:
    def __init__(self, window, window_title, video_sources=['arrived_car.mp4', 'waiting_people.mp4']):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1800x1100")

        self.canvas_width = 250
        self.canvas_height = 325
        self.vids = {
            'left_car': VideoCapture(video_sources[0]),
            'people': VideoCapture(video_sources[1]),
            # 'right_car': VideoCapture(video_sources[0])
        }

        self.places = {
            'left_car': [self.canvas_width + 10, 10],
            'people': [10, self.canvas_height + 10],
            # 'right_car': [self.canvas_width*2+10, self.canvas_height+10]
        }
        self.photos = {}
        self.last_red = datetime.now()
        self.last_green = datetime.now()
        self.car_traffic_lights = {
            'x1' :TrafficLight(self.window, 360, 470, 70, 190),
            'x2' :TrafficLight(self.window, 1000, 300, 70, 190),
            'y1' :TrafficLight(self.window, 500, 170, 70, 190),
            'y2' :TrafficLight(self.window, 800, 570, 70, 190),
        }
        # self.traffic_light.gogreen()

        self.canvases = {}
        self.add_video_change_buttons(10, 700, 'Play clear pavement', 'people', 'clear_pavement.mp4')
        self.add_video_change_buttons(10, 730, 'Play waiting people', 'people', 'waiting_people.mp4')

        self.add_video_change_buttons(500, 30, 'Play arrived car', 'left_car', 'arrived_car.mp4')
        self.add_video_change_buttons(500, 60, 'Play clear road', 'left_car', 'clear_road.mp4')

        for key in self.vids.keys():
            canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
            canvas.place(
                x=self.places[key][0],
                y=self.places[key][1],
                width=self.canvas_width,
                height=self.canvas_height
            )
            self.canvases[key] = canvas

        self.delay = 30
        self.update_video_frame()

        self.window.mainloop()

    def update_video_frame(self):
        objects_cnt = {}
        for key in self.vids.keys():
            frame, object_cnt = self.vids[key].get_frame()
            objects_cnt[key] = object_cnt

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(resized_image)
            self.canvases[key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[key] = photo

        self.update_traffic_light(objects_cnt)
        self.window.after(self.delay, self.update_video_frame)

    def update_traffic_light(self, objects_cnt):
        if (sum_values_by_key_pattern(objects_cnt, r'car') > 0
                and sum_values_by_key_pattern(objects_cnt, r'people') > 0
                and datetime.now() - self.last_red > timedelta(seconds=50))\
                or (sum_values_by_key_pattern(objects_cnt, r'car') == 0
                    and sum_values_by_key_pattern(objects_cnt, r'people') > 0
                    and datetime.now() - self.last_red > timedelta(seconds=20)):
            self.traffic_light.gored()
            self.last_red = datetime.now()
        elif (sum_values_by_key_pattern(objects_cnt, r'car') > 0
              and datetime.now() - self.last_green > timedelta(seconds=20)):
            self.traffic_light.gogreen()
            self.last_green = datetime.now()
        # else:

    def add_video_change_buttons(self, button_x, button_y, text, video_key, new_video_path):
        button = tkinter.Button(self.window, text=text,
                                command=lambda: self.change_video_source(video_key, new_video_path))
        button.place(x=button_x, y=button_y)

    def change_video_source(self, video_key, new_source):
        if video_key in self.vids:
            self.vids[video_key].set_vid(new_source)
        else:
            print(f"No video source found for key: {video_key}")


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV")
