from datetime import datetime
from tkinter import *


class TrafficLight():

    def __init__(self, window):
        self.window = window
        self.last_changed_at = datetime.now()
        self.canvases = {}
        self.with_yellow_color = {}
        self.ovals = {}
        # self.add_traffic_light(canvas_name, x, y, width, height, with_yellow_color=with_yellow_color)

    def add_traffic_light(self, canvas_name, x, y, width, height, with_yellow_color=True):
        self.green_state = GreenState(self)
        self.with_yellow_color[canvas_name] = with_yellow_color
        if self.with_yellow_color[canvas_name]:
            self.yellow_state = YellowState(self)
        self.red_state = RedState(self)

        self.canvases[canvas_name] = Canvas(self.window, width=width, height=height, bg="#003366")
        self.canvases[canvas_name].place(x=x, y=y)

        self.resize_ovals(canvas_name)

        self.canvases[canvas_name].bind("<Configure>", lambda event, c=canvas_name: self.on_resize(event, c))



    def resize_ovals(self, canvas_name):
        # Установка ширины и высоты кругов светофора равными для создания идеального круга
        oval_size = self.canvases[canvas_name].winfo_width() * 0.75
        x0 = (self.canvases[canvas_name].winfo_width() - oval_size) / 2

        # Расчет фиксированного отступа между кругами на основе размера круга
        spacing = oval_size * 0.1

        # Начальное положение первого круга
        y0 = spacing
        y1 = y0 + oval_size + spacing
        y2 = y1 + oval_size + spacing


        self.ovals[canvas_name] = {}
        kw = {'fill': "white", 'outline': "black"}
        # kw = {'outline': "black"}
        self.ovals[canvas_name]['red'] = self.canvases[canvas_name].create_oval(x0, y0, x0 + oval_size, y0 + oval_size, **kw)
        # self.ovals['red'] = self.canvases[canvas_name].create_oval(x0, y0, x0 + oval_size, y0 + oval_size, fill='red' , **kw)
        if self.with_yellow_color[canvas_name]:
            # self.ovals['yellow'] = self.canvases[canvas_name].create_oval(x0, y1, x0 + oval_size, y1 + oval_size, fill='yellow', **kw)
            self.ovals[canvas_name]['yellow'] = self.canvases[canvas_name].create_oval(x0, y1, x0 + oval_size, y1 + oval_size, **kw)
        else:
            y2 = y1
        # self.ovals['green'] = self.canvases[canvas_name].create_oval(x0, y2, x0 + oval_size, y2 + oval_size, fill='green', **kw)
        self.ovals[canvas_name]['green'] = self.canvases[canvas_name].create_oval(x0, y2, x0 + oval_size, y2 + oval_size, **kw)

    def on_resize(self, event, canvas_name):
        self.canvases[canvas_name].delete("all")
        self.resize_ovals(canvas_name)

    def gored(self):
        self.change_color('green', self.red_state.handle_request)

    def gogreen(self):
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
                self.yellow_state.handle_request(self)

        if blink_cnt <= 12:
            self.window.after(500, self.change_color, from_color, handle_request, blink_cnt + 1)
        else:
            self.window.after(500, handle_request, self)

    # def __str__(self):
    #     return '{} {} {} {}'.format(self.green_state, self.yellow_state, self.red_state, self.state)


class State():

    def handle_request(self):
        pass

    def __str__(self):
        return 'Abstract method'


class RedState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, refer):
        print('Wait for turning traffic light to green...')
        for canvas_name in refer.canvases.keys():
            refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['red'], fill="red")
            if refer.with_yellow_color[canvas_name]:
                refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['yellow'], fill="white")
            refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on red.'


class YellowState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, refer):
        print('Wait for turning traffic light to red...')
        for canvas_name in refer.canvases.keys():
            if refer.with_yellow_color[canvas_name]:
                refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['red'], fill="white")
                refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['yellow'], fill="yellow")
                refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on yellow.'


class GreenState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, refer):
        for canvas_name in refer.canvases.keys():
            refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['red'], fill="white")
            if refer.with_yellow_color[canvas_name]:
                refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['yellow'], fill="white")
            refer.canvases[canvas_name].itemconfig(refer.ovals[canvas_name]['green'], fill="green")

    def __str__(self):
        return 'Traffic light is on green.'
