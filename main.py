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
        self.window.geometry("1800x1100")

        self.canvas_width = 200
        self.canvas_height = 290
        self.x_traffic_light = TrafficLight(self.window)
        self.y_traffic_light = TrafficLight(self.window)
        self.models = {
            'car_x1': {
                'video': VideoCapture(video_sources[0]),
                'places': [170, 325],
                'buttons': [
                    self.add_video_change_buttons(5, 360, 'Play arrived car', 'car_x1', 'arrived_car.mp4'),
                    self.add_video_change_buttons(5, 390, 'Play clear road', 'car_x1', 'clear_road.mp4')
                ],
                'traffic_light': self.x_traffic_light.add_traffic_light('car_x1', 380, 420, 70, 190),
                'oriented': 'x'
            },
            'car_x2': {
                'video': VideoCapture(video_sources[3]),
                'places': [1350, 325],
                'buttons': [
                    self.add_video_change_buttons(1550, 360, 'Play arrived car', 'car_x2', 'arrived_car.mp4'),
                    self.add_video_change_buttons(1550, 390, 'Play clear road', 'car_x2', 'clear_road.mp4')
                ],
                'traffic_light': self.x_traffic_light.add_traffic_light('car_x2', 1250, 325, 70, 190),
                'oriented': 'x'
            },
            'car_y1': {
                'video': VideoCapture(video_sources[3]),
                'places': [650, 10],
                'buttons': [
                    self.add_video_change_buttons(850, 60, 'Play arrived car', 'car_x1', 'arrived_car.mp4'),
                    self.add_video_change_buttons(850, 90, 'Play clear road', 'car_x1', 'clear_road.mp4')
                ],
                'traffic_light': self.y_traffic_light.add_traffic_light('car_y1', 570, 170, 70, 190),
                'oriented': 'y'
            },
            'car_y2': {
                'video': VideoCapture(video_sources[3]),
                'places': [650, 700],
                'buttons': [
                    self.add_video_change_buttons(850, 870, 'Play arrived car', 'car_x1', 'arrived_car.mp4'),
                    self.add_video_change_buttons(850, 900, 'Play clear road', 'car_x1', 'clear_road.mp4')
                ],
                'traffic_light': self.y_traffic_light.add_traffic_light('car_y2', 850, 600, 70, 190),
                'oriented': 'y'
            },
            'people_x1y1': {
                'video': VideoCapture(video_sources[2]),
                'places': [170, 10],
                'buttons': [
                    self.add_video_change_buttons(5, 60, 'Play clear pavement', 'people_x1y1','clear_pavement.mp4'),
                    self.add_video_change_buttons(5, 90, 'Play waiting people', 'people_x1y1', 'waiting_people.mp4')
                ],
                'traffic_light': self.y_traffic_light.add_traffic_light('people_x1y1', 400, 130, 70, 130, False),
                'oriented': 'y'
            },
            # 'people_x2y1': {
            #     'video': VideoCapture(video_sources[2]),
            #     'places': [1350, 10],
            #     'buttons': [
            #         self.add_video_change_buttons(1550, 60, 'Play clear pavement', 'people_x2y1',
            #                                       'clear_pavement.mp4'),
            #         self.add_video_change_buttons(1550, 90, 'Play waiting people', 'people_x2y1',
            #                                       'waiting_people.mp4')
            #     ]
            # },
            # 'people_x1y2': {
            #     'video': VideoCapture(video_sources[1]),
            #     'places': [170, 700],
            #     'buttons': [
            #         self.add_video_change_buttons(5, 760, 'Play clear pavement', 'people_x1y2',
            #                                       'clear_pavement.mp4'),
            #         self.add_video_change_buttons(5, 790, 'Play waiting people', 'people_x1y2',
            #                                       'waiting_people.mp4')
            #     ]
            # },
            # 'people_x2y2': {
            #     'video': VideoCapture(video_sources[2]),
            #     'places': [1350, 700],
            #     'buttons': [
            #         self.add_video_change_buttons(1550, 760, 'Play clear pavement', 'people_x2y2',
            #                                       'clear_pavement.mp4'),
            #         self.add_video_change_buttons(1550, 790, 'Play waiting people', 'people_x2y2',
            #                                       'waiting_people.mp4')
            #     ]
            # },
        }
        # self.y_traffic_light.gogreen()
        # self.x_traffic_light.gored()
        self.y_traffic_light.gored()
        self.x_traffic_light.gogreen()

        self.photos = {}

        self.canvases = {}
        for model_key, model in self.models.items():
            canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
            canvas.place(
                x=model['places'][0],
                y=model['places'][1],
                width=self.canvas_width,
                height=self.canvas_height
            )
            self.canvases[model_key] = canvas

        self.delay = 30
        self.update_video_frame()

        self.window.mainloop()

    def update_video_frame(self):
        objects_cnt = {}
        for model_key, model in self.models.items():
            frame, object_cnt = model['video'].get_frame()
            objects_cnt[model['oriented']] = object_cnt + objects_cnt.get('oriented', 0)

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(resized_image)
            self.canvases[model_key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[model_key] = photo

        # self.update_traffic_light(objects_cnt)
        self.window.after(self.delay, self.update_video_frame)

    # def update_traffic_light(self, objects_cnt):
    #     if (objects_cnt['y'] > 0
    #             and objects_cnt['x'] > 0
    #             and datetime.now() - self.last_red > timedelta(seconds=50))\
    #             or (objects_cnt['x'] == 0
    #                 and objects_cnt['y'] > 0
    #                 and datetime.now() - self.last_red > timedelta(seconds=20)):
    #         self.traffic_light.gored()
    #         self.last_red = datetime.now()
    #     elif (sum_values_by_key_pattern(objects_cnt, r'car') > 0
    #           and datetime.now() - self.last_green > timedelta(seconds=20)):
    #         self.traffic_light.gogreen()
    #         self.last_green = datetime.now()
        # else:

    def add_video_change_buttons(self, button_x, button_y, text, video_key, new_video_path):
        button = tkinter.Button(self.window, text=text,
                                command=lambda: self.change_video_source(video_key, new_video_path))
        button.place(x=button_x, y=button_y)

    def change_video_source(self, video_key, new_source):
        if video_key in self.models:
            self.models[video_key]['video'].set_vid(new_source)
        else:
            print(f"No video source found for key: {video_key}")


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV")
