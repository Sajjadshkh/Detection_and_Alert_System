import cv2
import numpy as np

def detect_fire(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([0, 50, 50])
    upper_bound = np.array([10, 255, 255])
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    return cv2.countNonZero(mask) > 500