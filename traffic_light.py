from datetime import datetime
from tkinter import *


class TrafficLight():

    def __init__(self, window):
        self.window = window
        self.last_status_changed_at = datetime.now()
        self.canvases = {}
        self.with_yellow_color = {}
        self.ovals = {}
        self.oriented = {}

        self.green_state = GreenState(self)
        self.yellow_state = YellowState(self)
        self.red_state = RedState(self)

        self.traffic_states = [(True, False), (False, True)]
        self.traffic_state = 1

    def add_traffic_light(self, canvas_name, x, y, width, height, oriented, with_yellow_color=True):
        self.with_yellow_color[canvas_name] = with_yellow_color
        self.oriented[canvas_name] = oriented

        self.canvases[canvas_name] = Canvas(self.window, width=width, height=height, bg="#003366")
        self.canvases[canvas_name].place(x=x, y=y)

        self.resize_ovals(canvas_name)

        self.canvases[canvas_name].bind("<Configure>", lambda event, c=canvas_name: self.on_resize(event, c))

    def resize_ovals(self, canvas_name):
        oval_size = self.canvases[canvas_name].winfo_width() * 0.75
        x0 = (self.canvases[canvas_name].winfo_width() - oval_size) / 2

        spacing = oval_size * 0.1

        y0 = spacing
        y1 = y0 + oval_size + spacing
        y2 = y1 + oval_size + spacing

        self.ovals[canvas_name] = {}
        kw = {'fill': "white", 'outline': "black"}
        self.ovals[canvas_name]['red'] = self.canvases[canvas_name].create_oval(x0, y0, x0 + oval_size, y0 + oval_size, **kw)
        if self.with_yellow_color[canvas_name]:
            self.ovals[canvas_name]['yellow'] = self.canvases[canvas_name].create_oval(x0, y1, x0 + oval_size, y1 + oval_size, **kw)
        else:
            y2 = y1
        self.ovals[canvas_name]['green'] = self.canvases[canvas_name].create_oval(x0, y2, x0 + oval_size, y2 + oval_size, **kw)

    def on_resize(self, event, canvas_name):
        self.canvases[canvas_name].delete("all")
        self.resize_ovals(canvas_name)

    def handle_requests(self):
        for canvas_name in self.canvases.keys():
            if self.traffic_states[self.traffic_state % 2][self.oriented[canvas_name]]:
                self.green_state.handle_request(canvas_name)
            else:
                self.red_state.handle_request(canvas_name)

    def change_colors(self, blink_cnt=1):
        self.last_status_changed_at = datetime.now()
        for canvas_name in self.canvases.keys():
            if self.traffic_states[self.traffic_state][self.oriented[canvas_name]]:
                from_color = 'red'
            else:
                from_color = 'green'
            if blink_cnt <= 6 or (self.with_yellow_color[canvas_name] is False and blink_cnt <= 12):
                self.canvases[canvas_name].itemconfig(
                    self.ovals[canvas_name][from_color], fill=from_color if blink_cnt % 2 else "white"
                )
            elif self.with_yellow_color[canvas_name] and blink_cnt == 7:
                self.yellow_state.handle_request(canvas_name)

        if blink_cnt <= 12:
            self.window.after(500, self.change_colors, blink_cnt + 1)
        else:
            self.window.after(500, self.handle_requests)

class State():

    def handle_request(self):
        pass

    def __str__(self):
        return 'Abstract method'


class RedState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        print('Wait for turning traffic light to green...')
        self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="red")
        if self.traffic_light.with_yellow_color[canvas_name]:
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
        self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on red.'


class YellowState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        print('Wait for turning traffic light to red...')
        if self.traffic_light.with_yellow_color[canvas_name]:
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="yellow")
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on yellow.'


class GreenState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, canvas_name):
        self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
        if self.traffic_light.with_yellow_color[canvas_name]:
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
        self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="green")

    def __str__(self):
        return 'Traffic light is on green.'
