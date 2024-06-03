import re
import tkinter
from PIL import Image, ImageTk
import time

from model import class_names
from traffic_light import TrafficLight
from traffic_manager import manage_traffic_light
from traffic_stats_utils import reset_objects_in_areas_stats, merge_stats
from video_capture import VideoCapture


class Simulation:
    def __init__(self, window, window_title, config, priority, start_time):
        self.config = config
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1800x1100")

        self.priority = {
            class_names.index(tracked_object): priority for tracked_object, priority in priority.items()
        }
        self.start_time = start_time
        self.traffic_light = TrafficLight(self.window)

        self.min_change_time = 5

        self.models = self.create_models(self.config['models'])
        self.canvas_width = self.config['canvas']['width']
        self.canvas_height = self.config['canvas']['height']
        self.stopwatch_label = tkinter.Label(self.window, text="00:00:00", fg="black", font="Verdana 30 bold")
        self.stopwatch_label.place(x=700, y=350)
        self.direction_priorities_label = tkinter.Label(self.window, text='', font=('Arial', 24))
        self.direction_priorities_label.place(x=500, y=400)
        self.time_to_access_changing_traffic_signal = tkinter.Label(self.window, text='', font="Verdana 30 bold")
        self.time_to_access_changing_traffic_signal.place(x=700, y=450)

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
        self.photos = {}
        self.delay = 30
        self.update_video_frame()
        self.window.mainloop()

    def create_models(self, models_config):
        models = {}
        for model_name, settings in models_config.items():
            model = {
                'video': VideoCapture(settings['video_source'], settings['video_sources'], settings['tracked_objects']),
                'places': settings['places'],
                'buttons': self.add_video_change_buttons(
                    model_name,
                    settings['buttons'],
                    settings['video_sources']
                ),
            }
            for traffic_light in settings['traffic_lights']:
                self.traffic_light.add_traffic_light(
                    model_name,
                    f'{model_name}_{traffic_light["oriented"]}',
                    **traffic_light
                )
            models[model_name] = model
        return models

    def update_video_frame(self):
        current_time = time.time() - self.start_time
        hrs, mins, sec = int(current_time // 3600), int((current_time % 3600) // 60), int(current_time % 60)
        self.stopwatch_label.config(text="{:02d}:{:02d}:{:02d}".format(hrs, mins, sec))

        self.objects_in_areas_stats = reset_objects_in_areas_stats()

        for model_name, model in self.models.items():
            model['video'].get_frame()
            if model['video'].is_last_frame is False:
                frame = model['video'].analyze_objects()
                image = Image.fromarray(frame)
                resized_image = image.resize((self.canvas_width, self.canvas_height))

                photo = ImageTk.PhotoImage(resized_image)
                self.canvases[model_name].create_image(0, 0, image=photo, anchor=tkinter.NW)
                self.photos[model_name] = photo

            print(f'Detected objects in {model_name} model:', model['video'].objects_in_areas_stats)
            self.objects_in_areas_stats = merge_stats(
                self.objects_in_areas_stats,
                model['video'].objects_in_areas_stats,
                model_name
            )

        print('Objects in models stats:', self.objects_in_areas_stats)
        direction_priorities, time_to_access_changing_traffic_signal = manage_traffic_light(self.objects_in_areas_stats, self)

        priorities_text = ', '.join(f"{key}: {value}" for key, value in direction_priorities.items())
        print('priorities_text', priorities_text)
        print('priorities_text', time_to_access_changing_traffic_signal)
        self.direction_priorities_label.config(text=priorities_text)

        total_seconds = int(time_to_access_changing_traffic_signal.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.time_to_access_changing_traffic_signal.config(text=time_str)

        self.window.after(self.delay, self.update_video_frame)

    def add_video_change_buttons(self, model_name, buttons_settings, video_sources):
        button_x = buttons_settings['button_x']
        button_y = buttons_settings['button_y']

        for key, value in video_sources.items():
            if isinstance(value, list):
                for video_source in value:
                    self.create_button(model_name, video_source, button_x, button_y)
                    button_y += 30
            else:
                self.create_button(model_name, value, button_x, button_y)
                button_y += 30

    def create_button(self, model_name, video_source, button_x, button_y):
        match = re.search(r'video/(.+?)\.mp4', video_source)
        if match:
            video_name = match.group(1)
            button = tkinter.Button(
                self.window,
                text=f'Play {video_name}',
                command=lambda vs=video_source: self.change_video_source(model_name, vs)
            )
            button.place(x=button_x, y=button_y)
        else:
            print(f"Invalid video source format: {video_source}")

    def change_video_source(self, video_key, new_source=None, video_type=None):
        if video_key in self.models:
            self.models[video_key]['video'].set_vid(new_source, video_type)
            self.models[video_key]['video'].mask = None
        else:
            print(f"No video source found for key: {video_key}")
