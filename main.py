import tkinter
import yaml
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import time
from traffic_light import TrafficLight
from video_utils import VideoCapture


class App:
    def __init__(
            self,
            window,
            window_title,
    ):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1800x1100")

        self.traffic_light = TrafficLight(self.window)

        with open('config.yml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.models = self.create_models(self.config['models'])
        self.canvas_width = self.config['canvas']['width']
        self.canvas_height = self.config['canvas']['height']
        self.stopwatch_label = tkinter.Label(self.window, text="00:00:00", fg="black", font="Verdana 30 bold")
        self.stopwatch_label.place(x=700, y=350)
        self.traffic_light.change_colors(application=self)
        self.photos = {}
        self.start_time = time.time()

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

    def create_models(self, models_config):
        models = {}
        for model_name, settings in models_config.items():
            model = {
                'video': VideoCapture(settings['video_source'], settings['tracked_objects']),
                'places': settings['places'],
                'buttons': [self.add_video_change_buttons(video_key=model_name, **button) for button in
                            settings['buttons']],
                'traffic_light': self.traffic_light.add_traffic_light(model_name, **settings['traffic_light']),
                'oriented': settings['traffic_light']['oriented']
            }
            models[model_name] = model
        return models

    def update_video_frame(self):
        current_time = time.time() - self.start_time
        hrs, mins, sec = int(current_time // 3600), int((current_time % 3600) // 60), int(current_time % 60)
        self.stopwatch_label.config(text="{:02d}:{:02d}:{:02d}".format(hrs, mins, sec))

        objects_cnt = {}
        for model_key, model in self.models.items():
            frame, object_cnt = model['video'].get_frame()
            objects_cnt[model['oriented']] = object_cnt + objects_cnt.get(model['oriented'], 0)

            image = Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height))

            photo = ImageTk.PhotoImage(resized_image)
            self.canvases[model_key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[model_key] = photo

        self.update_traffic_light(objects_cnt)
        self.window.after(self.delay, self.update_video_frame)

    def update_traffic_light(self, objects_cnt):
        if (objects_cnt[1] > 0 and objects_cnt[0] == 0
                and datetime.now() - self.traffic_light.last_status_changed_at > timedelta(seconds=10)
                and self.traffic_light.traffic_state != 1):
            self.traffic_light.traffic_state = 1
            self.traffic_light.change_colors(application=self)
        elif (objects_cnt[1] == 0 and objects_cnt[0] > 0
              and datetime.now() - self.traffic_light.last_status_changed_at > timedelta(seconds=10)
                and self.traffic_light.traffic_state != 0):
            self.traffic_light.traffic_state = 0
            self.traffic_light.change_colors(application=self)
        elif (objects_cnt[1] > 0 and objects_cnt[0] > 0
              and datetime.now() - self.traffic_light.last_status_changed_at > timedelta(seconds=20)):
            if self.traffic_light.traffic_state == 0:
                self.traffic_light.traffic_state = 1
                self.traffic_light.change_colors(application=self)
            elif self.traffic_light.traffic_state == 1:
                self.traffic_light.traffic_state = 0
                self.traffic_light.change_colors(application=self)
        elif datetime.now() - self.traffic_light.last_status_changed_at > timedelta(seconds=30):
            self.traffic_light.change_colors(application=self)

    def add_video_change_buttons(self, button_x, button_y, label, video_key, video_path):
        button = tkinter.Button(self.window, text=label,
                                command=lambda: self.change_video_source(video_key, video_path))
        button.place(x=button_x, y=button_y)

    def change_video_source(self, video_key, new_source):
        if video_key in self.models:
            self.models[video_key]['video'].set_vid(new_source)
        else:
            print(f"No video source found for key: {video_key}")


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    application = App(tkinter.Tk(), "Tkinter and OpenCV")
