import time
from tkinter import *


class TrafficLight():

    def __init__(self, window, x, y, width, height):
        self.window = window
        self.green_state = GreenState(self)
        self.yellow_state = YellowState(self)
        self.red_state = RedState(self)
        self.width = width
        self.height = height

        self.canvas = Canvas(window, width=self.width, height=self.height, bg="#003366")
        self.canvas.place(x=x, y=y)

        self.resize_ovals()

        self.canvas.bind("<Configure>", self.on_resize)

    def resize_ovals(self):
        # Установка ширины и высоты кругов светофора равными для создания идеального круга
        oval_size = self.canvas.winfo_width() * 0.75
        x0 = (self.canvas.winfo_width() - oval_size) / 2

        # Расчет фиксированного отступа между кругами на основе размера круга
        spacing = oval_size * 0.1

        y0 = spacing
        y1 = y0 + oval_size + spacing
        y2 = y1 + oval_size + spacing

        self.ovals = {
            'red': self.canvas.create_oval(x0, y0, x0 + oval_size, y0 + oval_size, fill="white", outline="black"),
            'yellow': self.canvas.create_oval(x0, y1, x0 + oval_size, y1 + oval_size, fill="white", outline="black"),
            'green': self.canvas.create_oval(x0, y2, x0 + oval_size, y2 + oval_size, fill="white", outline="black")
        }

    def on_resize(self, event):
        # При изменении размера окна пересоздаем овалы
        self.canvas.delete("all")
        self.resize_ovals()

    def gored(self):
        self.change_color('green', 'red', self.red_state.handle_request)

    def gogreen(self):
        self.change_color('red','green', self.green_state.handle_request)

    def __goyellow(self, handle_request, refer):
        time_interval = 3000
        self.yellow_state.handle_request(self)
        self.window.after(time_interval, handle_request, self)

    def change_color(self, from_color, to_color, handle_request, blink_cnt=1):
        if blink_cnt <= 6:
            self.canvas.itemconfig(self.ovals[from_color], fill="white" if blink_cnt % 2 else from_color)
            self.window.after(500, self.change_color, from_color, to_color, handle_request, blink_cnt + 1)
        else:
            self.canvas.itemconfig(self.ovals[from_color], fill=from_color)
            self.window.after(500, self.__goyellow, handle_request, self)

    def __str__(self):
        return '{} {} {} {}'.format(self.green_state, self.yellow_state, self.red_state, self.state)


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
        # self.traffic_light.set_state(self.traffic_light.get_green_light_state())
        refer.canvas.itemconfig(refer.ovals['red'], fill="red")
        refer.canvas.itemconfig(refer.ovals['yellow'], fill="white")
        refer.canvas.itemconfig(refer.ovals['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on red.'


class YellowState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, refer):
        print('Wait for turning traffic light to red...')
        # self.traffic_light.set_state(self.traffic_light.get_red_light_state()
        refer.canvas.itemconfig(refer.ovals['red'], fill="white")
        refer.canvas.itemconfig(refer.ovals['yellow'], fill="yellow")
        refer.canvas.itemconfig(refer.ovals['green'], fill="white")

    def __str__(self):
        return 'Traffic light is on yellow.'


class GreenState(State):

    def __init__(self, traffic_light):
        self.traffic_light = traffic_light

    def handle_request(self, refer):
        print('Wait for turning traffic light to yellow...')
        # self.traffic_light.set_state(self.traffic_light.get_yellow_light_state())
        refer.canvas.itemconfig(refer.ovals['red'], fill="white")
        refer.canvas.itemconfig(refer.ovals['yellow'], fill="white")
        refer.canvas.itemconfig(refer.ovals['green'], fill="green")

    def __str__(self):
        return 'Traffic light is on green.'
