import tkinter
import PIL.Image, PIL.ImageTk
from datetime import datetime, timedelta
from traffic_light import TrafficLight
from traffic_utils import sum_values_by_key_pattern
from video_utils import VideoCapture


class App:
    def __init__(
            self,
            window,
            window_title,
            video_sources=['arrived_car.mp4', 'waiting_people.mp4', 'clear_pavement.mp4', 'clear_road.mp4']
    ):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1700x1100")

        self.canvas_width = 200
        self.canvas_height = 290
        self.vids = {
            'car_x1': {
                'video': VideoCapture(video_sources[0]),
                'places': [170, 325],
                'buttons': [
                    self.add_video_change_buttons(5, 360, 'Play arrived car', 'car_x1', 'arrived_car.mp4'),
                    self.add_video_change_buttons(5, 390, 'Play clear road', 'car_x1', 'clear_road.mp4')
                ]
            },
            'car_x2': {
                'video': VideoCapture(video_sources[3]),
                'places': [1350, 325],
                'buttons': [
                    self.add_video_change_buttons(1550, 360, 'Play arrived car', 'car_x2', 'arrived_car.mp4'),
                    self.add_video_change_buttons(1550, 390, 'Play clear road', 'car_x2', 'clear_road.mp4')
                ]
            },
            'car_y1': {
                'video': VideoCapture(video_sources[3]),
                'places': [650, 10],
            },
            'car_y2': {
                'video': VideoCapture(video_sources[3]),
                'places': [650, 700],
            },
            'people_x1y1': {
                'video': VideoCapture(video_sources[2]),
                'places': [170, 10],
                'buttons': [
                    self.add_video_change_buttons(5, 60, 'Play clear pavement', 'people_x1y1', 'clear_pavement.mp4'),
                    self.add_video_change_buttons(5, 90, 'Play waiting people', 'people_x1y1', 'waiting_people.mp4')
                ]
            },
            'people_x2y1': {
                'video': VideoCapture(video_sources[2]),
                'places': [1350, 10],
            },
            'people_x1y2': {
                'video': VideoCapture(video_sources[1]),
                'places': [170, 700],
            },
            'people_x2y2': {
                'video': VideoCapture(video_sources[2]),
                'places': [1350, 700],
            },
        }
        self.car_traffic_lights = {
            'x': {
                'x1' :TrafficLight(self.window, 380, 420, 70, 190),
                'x2' :TrafficLight(self.window, 1250, 325, 70, 190),
            },
            'y': {
                'y1' :TrafficLight(self.window, 570, 170, 70, 190),
                'y2' :TrafficLight(self.window, 850, 600, 70, 190),
            }
        }
        for traffic_light in self.car_traffic_lights['x'].values():
            traffic_light.gogreen()

        for traffic_light in self.car_traffic_lights['y'].values():
            traffic_light.gored()


        # self.add_video_change_buttons(10, 700, 'Play clear pavement', 'people', 'clear_pavement.mp4')
        # self.add_video_change_buttons(10, 730, 'Play waiting people', 'people', 'waiting_people.mp4')
        #
        # self.add_video_change_buttons(500, 30, 'Play arrived car', 'left_car', 'arrived_car.mp4')
        # self.add_video_change_buttons(500, 60, 'Play clear road', 'left_car', 'clear_road.mp4')

        self.photos = {}
        self.last_red = datetime.now()
        self.last_green = datetime.now()

        self.canvases = {}

        for key in self.vids.keys():
            canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
            canvas.place(
                x=self.vids[key]['places'][0],
                y=self.vids[key]['places'][1],
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
            frame, object_cnt = self.vids[key]['video'].get_frame()
            objects_cnt[key] = object_cnt

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(resized_image)
            self.canvases[key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[key] = photo

        # self.update_traffic_light(objects_cnt)
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
            self.vids[video_key]['video'].set_vid(new_source)
        else:
            print(f"No video source found for key: {video_key}")


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV")
