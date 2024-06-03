import yaml
import time

from production_traffic_manager_app import ProductionTrafficManagerApp
from simulation import Simulation
from model import class_names


class App:
    def __init__(
            self,
            config_path,
            is_simulation,
            window_title,
    ):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)

        self.priority = {
            class_names.index(tracked_object): priority for tracked_object, priority in self.config['priority'].items()
        }

        self.start_time = time.time()
        self.is_simulation = is_simulation
        if is_simulation:
            import tkinter

            Simulation(tkinter.Tk(), window_title, self.config, self.priority, self.start_time)
        else:
            ProductionTrafficManagerApp(self.config, self.priority, self.start_time)
