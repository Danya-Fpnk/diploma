from model import class_names
from real_time_video_capture import RealTimeVideoCapture
from traffic_manager import manage_traffic_light
from traffic_stats_utils import reset_objects_in_areas_stats, merge_stats


class ProductionTrafficManagerApp:
    def __init__(self, config, priority, start_time):
        self.config = config
        self.priority = {
            class_names.index(tracked_object): priority for tracked_object, priority in priority.items()
        }
        self.start_time = start_time

        self.traffic_lights = None
        self.video_objects = {}

        for model_name, settings in config.items():
            video_object = {
                'video': RealTimeVideoCapture(settings['video_source'], settings['video_sources'], settings['tracked_objects']),
                # 'traffic_light': self.traffic_light.add_traffic_light(model_name, **settings['traffic_light']),
            }
            self.video_objects[model_name] = video_object

    def create_video_captures(self, video_capture_config):
        models = {}
        for model_name, settings in video_capture_config.items():
            model = {
                'video': RealTimeVideoCapture(settings['video_source'], settings['video_sources'], settings['tracked_objects']),
                # 'traffic_light': self.traffic_light.add_traffic_light(model_name, **settings['traffic_light']),
            }
            models[model_name] = model
        return models

    def update_video_frame(self):
        while True:
            self.objects_in_areas_stats = reset_objects_in_areas_stats()

            for model_name, model in self.models.items():
                model['video'].get_frame()
                if model['video'].is_last_frame is False:
                    model['video'].analyze_objects()

                self.objects_in_areas_stats = merge_stats(
                    self.objects_in_areas_stats,
                    model['video'].objects_in_areas_stats,
                    model_name
                )

            if self.traffic_lights:
                manage_traffic_light(self.objects_in_areas_stats, self.traffic_lights)

