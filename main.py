import tkinter
import PIL.Image, PIL.ImageTk
from traffic_light import TrafficLight
from traffic_utils import sum_values_by_key_pattern
from video_utils import VideoCapture


class App:
    def __init__(self, window, window_title, video_sources=['arrived_car.mp4', 'waiting_people.mp4']):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1600x1000")

        self.canvas_width = 250
        self.canvas_height = 325
        self.vids = {
            'left_car': VideoCapture(video_sources[0]),
            'people': VideoCapture(video_sources[1]),
            # 'right_car': VideoCapture(video_sources[0])
        }

        self.places = {
            'left_car': [10, self.canvas_height+10],
            'people': [self.canvas_width+10, 10],
            # 'right_car': [self.canvas_width*2+10, self.canvas_height+10]
        }
        self.photos = {}

        self.canvases = {}
        # self.add_video_change_buttons()

        for key in self.vids.keys():
            canvas = tkinter.Canvas(self.window, width=self.canvas_width, height=self.canvas_height)
            canvas.place(
                x=self.places[key][0],
                y=self.places[key][1],
                width=self.canvas_width,
                height=self.canvas_height
            )
            self.canvases[key] = canvas

        TrafficLight(self.window)

        self.delay = 30
        self.update_video_frame()

        self.window.mainloop()

    def get_intersection_stats(self, object_cnt):
        people_count = sum_values_by_key_pattern(object_cnt, r'people')
        car_count = sum_values_by_key_pattern(object_cnt, r'car')

        return people_count / car_count if car_count != 0 else 1

    def update_video_frame(self):
        objects_cnt = {}
        for key in self.vids.keys():
            frame, object_cnt = self.vids[key].get_frame()
            objects_cnt[key] = object_cnt

            image = PIL.Image.fromarray(frame)
            resized_image = image.resize((self.canvas_width, self.canvas_height), PIL.Image.LANCZOS)

            photo = PIL.ImageTk.PhotoImage(resized_image)
            self.canvases[key].create_image(0, 0, image=photo, anchor=tkinter.NW)
            self.photos[key] = photo

        # self.update_traffic_light()
        self.window.after(self.delay, self.update_video_frame)

    def update_traffic_light(self):
        pass

    def add_video_change_buttons(self, source=0):
        button_x = 10
        button_y = 700
        button_gap = 30
        for key in self.vids:
            button = tkinter.Button(self.window, text=f"Change {key} Video",
                                    command=lambda k=key: self.change_video_source(k, 'walking_people.mp4'))
            button.place(x=button_x, y=button_y)
            button_y += button_gap

    def change_video_source(self, video_key, new_source):
        if video_key in self.vids:
            self.vids[video_key].set_vid(new_source)
        else:
            print(f"No video source found for key: {video_key}")


if __name__ == "__main__":
    # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV")
