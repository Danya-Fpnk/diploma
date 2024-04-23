import tkinter
import yaml
import PIL.Image, PIL.ImageTk
from datetime import datetime, timedelta
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

        self.canvas_width = 200
        self.canvas_height = 290
        self.x_traffic_light = TrafficLight(self.window)
        self.y_traffic_light = TrafficLight(self.window)

        with open('config.yml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.models = self.create_models(self.config['models'])

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

    def create_models(self, models_config):
        models = {}
        for model_name, settings in models_config.items():
            model = {
                'video': VideoCapture(settings['video_source']),
                'places': settings['places'],
                'buttons': [self.add_video_change_buttons(video_key=model_name, **button) for button in
                            settings['buttons']],
                'traffic_light': self.x_traffic_light.add_traffic_light(model_name, **settings['traffic_light'])
                if settings['oriented'] == 'y' else self.y_traffic_light.add_traffic_light(
                    model_name, **settings['traffic_light']),
                'oriented': settings['oriented']
            }
            models[model_name] = model
        return models

    def update_video_frame(self):
        objects_cnt = {}
        for model_key, model in self.models.items():
            frame, object_cnt = model['video'].get_frame()
            objects_cnt[model['oriented']] = object_cnt + objects_cnt.get(model['oriented'], 0)

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(resized_image)
            self.canvases[model_key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[model_key] = photo

        self.update_traffic_light(objects_cnt)
        self.window.after(self.delay, self.update_video_frame)

    def update_traffic_light(self, objects_cnt):
        if (objects_cnt['x'] > 0 and objects_cnt['y'] == 0
                and datetime.now() - self.x_traffic_light.last_status_changed_at > timedelta(seconds=10)):
            self.x_traffic_light.gogreen()
            self.y_traffic_light.gored()
        elif (objects_cnt['x'] == 0 and objects_cnt['y'] > 0
              and datetime.now() - self.x_traffic_light.last_status_changed_at > timedelta(seconds=10)):
            self.x_traffic_light.gored()
            self.y_traffic_light.gogreen()
        elif (objects_cnt['x'] > 0 and objects_cnt['y'] > 0
              and datetime.now() - self.x_traffic_light.last_status_changed_at > timedelta(seconds=30)):
            if self.x_traffic_light.traffic_state == 'green':
                self.x_traffic_light.gored()
                self.y_traffic_light.gogreen()
            elif self.x_traffic_light.traffic_state == 'red':
                self.y_traffic_light.gored()
                self.x_traffic_light.gogreen()

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
    App(tkinter.Tk(), "Tkinter and OpenCV")
