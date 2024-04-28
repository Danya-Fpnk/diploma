import supervision as sv
import cv2


def main(file_name):
    generator = sv.get_video_frames_generator(f"{file_name}.mp4")
    iterator = iter(generator)
    frame = next(iterator)

    cv2.imwrite(f"../frame_for_select_detected_zone/{file_name}.jpg", frame)


if __name__ == "__main__":
    file_names = \
        [
            'straight_0_left_1',
            'straight_0_left_2',
            'straight_1_left_0',
            'straight_2_left_0',
            'straight_4_left_0',
            'straight_6_left_0',
            'straight_8_left_0',
        ]
    #     'arrived_car'
    #     'clear_pavement',
    #     'stop_car',
    #     'waiting_car',
    #     'walking_people',
    #     'arrived_car',
    #     'clear_road',
    #     'traffic_road',
    #     'waiting_people',
    # ]
    for file_name in file_names:
        main(file_name)
