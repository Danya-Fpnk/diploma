from datetime import datetime
from logging import exception
from tkinter import *


class TrafficLight():
    traffic_lights = []
    def __init__(self, window):
        self.window = window
        self.last_status_changed_at = datetime.now()
        self.canvases = {}
        self.ovals = {}
        self.oriented = {}

        self.green_state = GreenState(self)
        self.yellow_state = YellowState(self)
        self.red_state = RedState(self)
        self.priority_direction = None

        self.traffic_lights.append(self)

    def add_traffic_light(self, model_name, canvas_name, x, y, width, height, oriented, with_yellow_color=True):
        self.oriented[canvas_name] = oriented

        self.canvases[canvas_name] = {
            'canvas': Canvas(self.window, width=width, height=height, bg="#003366"),
            'oriented': oriented,
            'with_yellow_color': with_yellow_color,
            'state': 'yellow',
            'model_name': model_name
        }
        self.canvases[canvas_name]['canvas'].place(x=x, y=y)

        self.resize_ovals(canvas_name)

        self.canvases[canvas_name]['canvas'].bind("<Configure>", lambda event, c=canvas_name: self.on_resize(event, c))

    def resize_ovals(self, canvas_name):
        oval_size = self.canvases[canvas_name]['canvas'].winfo_width() * 0.75
        x0 = (self.canvases[canvas_name]['canvas'].winfo_width() - oval_size) / 2

        spacing = oval_size * 0.1

        y0 = spacing
        y1 = y0 + oval_size + spacing
        y2 = y1 + oval_size + spacing

        self.ovals[canvas_name] = {}
        kw = {'fill': "white", 'outline': "black"}
        self.ovals[canvas_name]['red'] = self.canvases[canvas_name]['canvas'].create_oval(
            x0, y0, x0 + oval_size, y0 + oval_size, **kw
        )
        if self.canvases[canvas_name]['with_yellow_color']:
            self.ovals[canvas_name]['yellow'] = self.canvases[canvas_name]['canvas'].create_oval(
                x0, y1, x0 + oval_size, y1 + oval_size, fill='yellow', outline='black'
            )
        else:
            y2 = y1
        self.ovals[canvas_name]['green'] = self.canvases[canvas_name]['canvas'].create_oval(
            x0, y2, x0 + oval_size, y2 + oval_size, **kw
        )

    def on_resize(self, event, canvas_name):
        self.canvases[canvas_name]['canvas'].delete("all")
        self.resize_ovals(canvas_name)

    def handle_requests(self, oriented_to_green):
        print(f'Turning traffic light to green for {oriented_to_green} orientation...')
        for canvas_name in self.canvases.keys():
            if self.canvases[canvas_name]['oriented'] == oriented_to_green:
                self.green_state.handle_request(canvas_name)
            else:
                self.red_state.handle_request(canvas_name)

    def update_models_video_sources(self, application, oriented_to_green):
        for canvas_name in self.canvases.keys():
            video_type = ("clear" if self.canvases[canvas_name]['oriented'] == oriented_to_green else "busy")
            application.change_video_source(self.canvases[canvas_name]['model_name'], video_type=video_type)

    def _change_colors(self, oriented_to_green, application, blink_cnt):
        for canvas_name in self.canvases.keys():
            if self.canvases[canvas_name]['oriented'] == oriented_to_green:
                if self.canvases[canvas_name]['state'] == 'red':
                    from_color = 'red'
                elif self.canvases[canvas_name]['state'] == 'yellow' and blink_cnt < 2:
                    blink_cnt = 14
                    break
                elif self.canvases[canvas_name]['state'] == 'green':
                    raise exception(f"Traffic light is already green: {self.canvases[canvas_name]['state']}")
            elif self.canvases[canvas_name]['state'] == 'green':
                from_color = 'green'
            else:
                continue
            if blink_cnt <= 6 or (self.canvases[canvas_name]['with_yellow_color'] is False and blink_cnt <= 12):
                self.canvases[canvas_name]['canvas'].itemconfig(
                    self.ovals[canvas_name][from_color], fill=from_color if blink_cnt % 2 else "white"
                )
            elif self.canvases[canvas_name]['with_yellow_color'] and blink_cnt == 7:
                self.yellow_state.handle_request(canvas_name)

        if blink_cnt <= 12:
            self.window.after(500, self._change_colors, oriented_to_green, application, blink_cnt + 1)
        else:
            self.window.after(1, self.handle_requests, oriented_to_green)
            self.window.after(3000, self.update_models_video_sources, application, oriented_to_green)

    def change_colors(self, oriented_to_green, application, blink_cnt=1,):
        self.last_status_changed_at = datetime.now()
        self.priority_direction = oriented_to_green
        self._change_colors(oriented_to_green, application, blink_cnt)


class State():

    def handle_request(self):
        pass

    def __str__(self):
        return 'Abstract method'


class RedState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        self.traffic_light.canvases[canvas_name]['state'] = 'red'
        self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="red")
        if self.traffic_light.canvases[canvas_name]['with_yellow_color']:
            self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
        self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on red.'


class YellowState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        self.traffic_light.canvases[canvas_name]['state'] = 'yellow'
        if self.traffic_light.canvases[canvas_name]['with_yellow_color']:
            self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
            self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="yellow")
            self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on yellow.'


class GreenState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        self.traffic_light.canvases[canvas_name]['state'] = 'green'
        self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
        if self.traffic_light.canvases[canvas_name]['with_yellow_color']:
            self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
        self.traffic_light.canvases[canvas_name]['canvas'].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="green")

    def __str__(self):
        return 'Traffic light is on green.'
