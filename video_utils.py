import cv2
import numpy as np


def dilate_polygon(polygon, dilation_size):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilation_size, dilation_size))
    dilated_polygon = cv2.dilate(polygon, kernel, iterations=1)
    return dilated_polygon


def add_mask_to_frame(mask, frame, dilation_size, video_areas):
    if mask is None:
        mask = np.zeros_like(frame)
        for area_key in video_areas.keys():
            polygon = np.array(video_areas[area_key], dtype=np.int32)
            dilated_mask = np.zeros_like(frame)
            cv2.fillPoly(dilated_mask, [polygon], (255,) * frame.shape[2])
            dilated_polygon = dilate_polygon(dilated_mask, dilation_size)
            mask = cv2.bitwise_or(mask, dilated_polygon)
    masked_frame = cv2.bitwise_and(frame, mask)
    return masked_frame, mask
