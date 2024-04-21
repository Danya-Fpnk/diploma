from datetime import datetime
from tkinter import *


class TrafficLight():

    def __init__(self, window):
        self.window = window
        self.last_status_changed_at = datetime.now()
        self.canvases = {}
        self.with_yellow_color = {}
        self.ovals = {}

        self.green_state = GreenState(self)
        self.yellow_state = YellowState(self)
        self.red_state = RedState(self)

        self.traffic_state = None

    def add_traffic_light(self, canvas_name, x, y, width, height, with_yellow_color=True):

        self.with_yellow_color[canvas_name] = with_yellow_color

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

    def gored(self):
        if self.traffic_state != 'red':
            self.traffic_state = 'red'
            self.change_color('green', self.red_state.handle_request)

    def gogreen(self):
        if self.traffic_state != 'green':
            self.traffic_state = 'green'
            self.change_color('red', self.green_state.handle_request)

    def change_color(self, from_color, handle_request, blink_cnt=1):
        for canvas_name in self.canvases.keys():
            if blink_cnt <= 6 or (self.with_yellow_color[canvas_name] is False and blink_cnt <= 12):
                if self.with_yellow_color[canvas_name] is False:
                    print('Changed color', canvas_name, 'to', from_color if blink_cnt % 2 else "white")
                self.canvases[canvas_name].itemconfig(
                    self.ovals[canvas_name][from_color], fill=from_color if blink_cnt % 2 else "white"
                )
            elif self.with_yellow_color[canvas_name] and blink_cnt == 7:
                self.yellow_state.handle_request()

        if blink_cnt <= 12:
            self.window.after(500, self.change_color, from_color, handle_request, blink_cnt + 1)
        else:
            self.window.after(500, handle_request)

class State():

    def handle_request(self):
        pass

    def __str__(self):
        return 'Abstract method'


class RedState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self):
        print('Wait for turning traffic light to green...')
        for canvas_name in self.traffic_light.canvases.keys():
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="red")
            if self.traffic_light.with_yellow_color[canvas_name]:
                self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")
        self.traffic_light.last_status_changed_at = datetime.now()

    def __str__(self):
        return 'Traffic light is on red.'


class YellowState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self):
        print('Wait for turning traffic light to red...')
        for canvas_name in self.traffic_light.canvases.keys():
            if self.traffic_light.with_yellow_color[canvas_name]:
                self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
                self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="yellow")
                self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="white")
        self.traffic_light.last_status_changed_at = datetime.now()

    def __str__(self):
        return 'Traffic light is on yellow.'


class GreenState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self):
        for canvas_name in self.traffic_light.canvases.keys():
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['red'], fill="white")
            if self.traffic_light.with_yellow_color[canvas_name]:
                self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['yellow'], fill="white")
            self.traffic_light.canvases[canvas_name].itemconfig(self.traffic_light.ovals[canvas_name]['green'], fill="green")
        self.traffic_light.last_status_changed_at = datetime.now()

    def __str__(self):
        return 'Traffic light is on green.'
