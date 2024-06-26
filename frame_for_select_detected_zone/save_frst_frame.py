import supervision as sv
import cv2


def main(file_name):
    generator = sv.get_video_frames_generator(f"../video/{file_name}.mp4")
    iterator = iter(generator)
    frame = next(iterator)

    cv2.imwrite(f"{file_name}.jpg", frame)


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
    for file_name in file_names:
        main(file_name)
