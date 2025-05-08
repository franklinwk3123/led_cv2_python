
import cv2
import numpy as np
from math import atan2, pi

def get_threshold_mask(gray):
    _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    return mask

def get_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea)

def get_ring_roi_from_contour(contour, image_shape, thickness=10):
    mask_outer = np.zeros(image_shape, dtype=np.uint8)
    cv2.drawContours(mask_outer, [contour], -1, 255, -1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
    mask_inner = cv2.erode(mask_outer, kernel, iterations=1)
    ring_roi = cv2.subtract(mask_outer, mask_inner)
    return ring_roi

def save_process_images(image, gray, mask, contour, roi_mask, folder_name):
    import os
    os.makedirs(folder_name, exist_ok=True)
    cv2.imwrite(f"{folder_name}/01_gray_image.png", gray)
    cv2.imwrite(f"{folder_name}/02_threshold_mask.png", mask)

    image_contour = image.copy()
    cv2.drawContours(image_contour, [contour], -1, (0, 255, 0), 2)
    cv2.imwrite(f"{folder_name}/03_contour_outline.png", image_contour)

    cv2.imwrite(f"{folder_name}/04_ring_roi_mask.png", roi_mask)

    overlay = image.copy()
    overlay[roi_mask > 0] = [0, 255, 255]
    cv2.imwrite(f"{folder_name}/05_overlay_roi_on_image.png", overlay)

def segment_ring_gray_roi(gray, roi_mask, num_segments=72):
    segment_values = [[] for _ in range(num_segments)]
    h, w = roi_mask.shape
    y_c, x_c = h // 2, w // 2
    ys, xs = np.where(roi_mask > 0)
    for x, y in zip(xs, ys):
        dx, dy = x - x_c, y - y_c
        theta = (atan2(dy, dx) + 2 * pi) % (2 * pi)
        index = int(theta / (2 * pi / num_segments))
        value = gray[y, x]
        segment_values[index].append(value)
    return [np.mean(s) if s else 0 for s in segment_values]

def segment_ring_rgb_roi(image_rgb, roi_mask, num_segments=72, channel=0):
    segment_values = [[] for _ in range(num_segments)]
    h, w = roi_mask.shape
    y_c, x_c = h // 2, w // 2
    ys, xs = np.where(roi_mask > 0)
    for x, y in zip(xs, ys):
        dx, dy = x - x_c, y - y_c
        theta = (atan2(dy, dx) + 2 * pi) % (2 * pi)
        index = int(theta / (2 * pi / num_segments))
        value = image_rgb[y, x, channel]
        segment_values[index].append(value)
    return [np.mean(s) if s else 0 for s in segment_values]
