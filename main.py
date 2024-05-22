import re
import tkinter
import yaml
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import time

from model import class_names
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

        self.priority = {
            class_names.index(tracked_object): priority for tracked_object, priority in self.config['priority'].items()
        }
        self.models = self.create_models(self.config['models'])
        self.canvas_width = self.config['canvas']['width']
        self.canvas_height = self.config['canvas']['height']
        self.stopwatch_label = tkinter.Label(self.window, text="00:00:00", fg="black", font="Verdana 30 bold")
        self.stopwatch_label.place(x=700, y=350)

        self.min_change_time = 5
        # self.traffic_light.change_colors(application=self)
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

        self.reset_objects_in_areas_stats()

        self.delay = 30
        self.update_video_frame()

        self.window.mainloop()

    def reset_objects_in_areas_stats(self):
        self.objects_in_areas_stats = {
            'detect_time': {}
        }

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
                'traffic_light': self.traffic_light.add_traffic_light(model_name, **settings['traffic_light']),
            }
            models[model_name] = model
        return models

    def merge_stats(self, new_stats, model_name):
        for area_key in new_stats['detect_time']:
            if area_key not in self.objects_in_areas_stats['detect_time']:
                self.objects_in_areas_stats['detect_time'][area_key] = {}
            for obj_class in new_stats['detect_time'][area_key].keys():
                if obj_class not in self.objects_in_areas_stats['detect_time'][area_key]:
                    self.objects_in_areas_stats['detect_time'][area_key][obj_class] = {}
                for track_id, detect_time in new_stats['detect_time'][area_key][obj_class].items():
                    self.objects_in_areas_stats['detect_time'][area_key][obj_class][f'{model_name}_{track_id}'] = detect_time

    def update_video_frame(self):
        current_time = time.time() - self.start_time
        hrs, mins, sec = int(current_time // 3600), int((current_time % 3600) // 60), int(current_time % 60)
        self.stopwatch_label.config(text="{:02d}:{:02d}:{:02d}".format(hrs, mins, sec))

        self.reset_objects_in_areas_stats()

        for model_name, model in self.models.items():
            model['video'].get_frame()
            if model['video'].is_last_frame is False:
                frame = model['video'].draw_objects()
                image = Image.fromarray(frame)
                resized_image = image.resize((self.canvas_width, self.canvas_height))

                photo = ImageTk.PhotoImage(resized_image)
                self.canvases[model_name].create_image(0, 0, image=photo, anchor=tkinter.NW)
                self.photos[model_name] = photo

            self.merge_stats(model['video'].objects_in_areas_stats, model_name)

        print(self.objects_in_areas_stats)
        self.update_traffic_light(self.objects_in_areas_stats)
        self.window.after(self.delay, self.update_video_frame)

    @staticmethod
    def calculate_min_time(objects_cnt, direction):
        base_time = 10
        extra_time_per_object = 1

        total_objects = sum(
            1
            for lane in objects_cnt['detect_time'][direction].values()
            for track_ids in lane.values()
        )
        return base_time + extra_time_per_object * total_objects

    def calculate_priority(self, current_unixtime, objects):
        total_priority = 0
        for obj_class, track_ids in objects.items():
            for track_id, detect_time in track_ids.items():
                wait_time = current_unixtime - detect_time
                wait_time_bonus = (wait_time // 5)
                total_priority += (self.priority.get(obj_class, 0) + wait_time_bonus)
        return total_priority

    def update_traffic_light(self, objects_in_areas_stats):
        current_unixtime = int(time.time())
        direction_priorities = {
            direction: self.calculate_priority(current_unixtime, objects)
            for direction, objects in objects_in_areas_stats['detect_time'].items()
        }
        current_time = datetime.now()
        max_priority_direction = max(direction_priorities, key=direction_priorities.get)


        print(direction_priorities)
        print(max_priority_direction)
        print(current_time - self.traffic_light.last_status_changed_at > timedelta(seconds=self.min_change_time))
        print(current_time - self.traffic_light.last_status_changed_at)
        print(timedelta(seconds=self.min_change_time))
        print(self.traffic_light.priority_direction != max_priority_direction)
        print(max_priority_direction)
        print(self.traffic_light.priority_direction)

        if (current_time - self.traffic_light.last_status_changed_at > timedelta(seconds=self.min_change_time)
                and self.traffic_light.priority_direction != max_priority_direction):
            self.min_change_time = self.calculate_min_time(objects_in_areas_stats, max_priority_direction)
            print('here')
            self.traffic_light.change_colors(max_priority_direction, application=self)

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


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    application = App(tkinter.Tk(), "Tkinter and OpenCV")



# {
#     'lst_in_waiting_area': {
#         'waiting_straight_area': {2: {1: 1715625088, 2: 1715625088}, 1: {}, 3: {}, 5: {}, 7: {}},
#         'waiting_left_area': {2: {1: 1715625088, 2: 1715625088}, 1: {}, 3: {}, 5: {}, 7: {}}},
#     'detect_time': {
#         'waiting_straight_area': {2: {1: 1715625080, 2: 1715625081}, 1: {}, 3: {}, 5: {}, 7: {}},
#         'waiting_left_area': {2: {1: 1715625080, 2: 1715625081}, 1: {}, 3: {}, 5: {}, 7: {}}
#     }
# }



# from ultralytics import YOLO
# from ultralytics.solutions import object_counter
# import cv2
#
# model = YOLO("yolov8n.pt")
# cap = cv2.VideoCapture("video/waiting_people.mp4")
# assert cap.isOpened(), "Error reading video file"
# w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
#
# line_points = [(20, 400), (1080, 400)]  # line or region points
# classes_to_count = [0, 2]  # person and car classes for count
#
# # Video writer
# video_writer = cv2.VideoWriter("waiting_people.avi",
#                        cv2.VideoWriter_fourcc(*'mp4v'),
#                        fps,
#                        (w, h))
#
# # Init Object Counter
# counter = object_counter.ObjectCounter()
# counter.set_args(view_img=True,
#                  reg_pts=line_points,
#                  classes_names=model.names,
#                  draw_tracks=True,
#                  line_thickness=2)
#
# while cap.isOpened():
#     success, im0 = cap.read()
#     if not success:
#         print("Video frame is empty or video processing has been successfully completed.")
#         break
#     tracks = model.track(im0, persist=True, show=False,
#                          classes=classes_to_count)
#
#     # print(tracks)
#     im0 = counter.start_counting(im0, tracks)
#     video_writer.write(im0)
#
# cap.release()
# video_writer.release()
# cv2.destroyAllWindows()