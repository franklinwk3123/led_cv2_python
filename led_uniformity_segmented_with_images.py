
import cv2
import os
import numpy as np
import pandas as pd
import sys
from math import atan2, pi
from datetime import datetime

def load_image_gray(path):
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray

def get_threshold_mask(gray):
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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

def segment_ring_roi(gray, roi_mask, num_segments=72):
    segment_brightness = [[] for _ in range(num_segments)]
    y_c, x_c = np.array(roi_mask.shape) // 2
    ys, xs = np.where(roi_mask > 0)

    for x, y in zip(xs, ys):
        dx, dy = x - x_c, y - y_c
        theta = (atan2(dy, dx) + 2 * pi) % (2 * pi)
        segment_index = int(theta / (2 * pi / num_segments))
        segment_brightness[segment_index].append(gray[y, x])

    brightness_avg = [np.mean(seg) if seg else 0 for seg in segment_brightness]
    return brightness_avg

def compute_uniformity(brightness_list):
    data = np.array(brightness_list)
    E_min = np.min(data)
    E_max = np.max(data)
    E_avg = np.mean(data)
    std_dev = np.std(data)
    uniformity = E_min / E_avg if E_avg > 0 else 0
    return uniformity, std_dev, E_min, E_avg, E_max

# --- 主程式 ---
if __name__ == "__main__":
    # === 設定參數 ===
    if len(sys.argv) != 2:
        print("⚠️ 使用方式: python test.py <圖片路徑>")
        exit(1)

    image_path = sys.argv[1]
    # 建立本地端資料夾
    folder_name = f"led_result_{os.path.splitext(os.path.basename(image_path))[0]}_{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(folder_name, exist_ok=True)
    image, gray = load_image_gray(image_path)
    mask = get_threshold_mask(gray)
    contour = get_largest_contour(mask)
    roi_mask = get_ring_roi_from_contour(contour, gray.shape, thickness=100)
    brightness_list = segment_ring_roi(gray, roi_mask, num_segments=72)
    uniformity, std_dev, E_min, E_avg, E_max = compute_uniformity(brightness_list)

    df = pd.DataFrame({
        "Segment": list(range(1, 73)),
        "Brightness": brightness_list
    })
    df.to_csv(f"{folder_name}/led_roi_brightness.csv", index=False)

    print(df)
    print(f"Uniformity (U₀): {uniformity:.4f}")
    print(f"Standard Deviation: {std_dev:.2f}")
    
    # === 儲存每階段圖像到資料夾 ===
    cv2.imwrite(f"{folder_name}/01_gray_image.png", gray)
    cv2.imwrite(f"{folder_name}/02_threshold_mask.png", mask)

    image_contour = image.copy()
    cv2.drawContours(image_contour, [contour], -1, (0, 255, 0), 2)
    cv2.imwrite(f"{folder_name}/03_contour_outline.png", image_contour)

    cv2.imwrite(f"{folder_name}/04_ring_roi_mask.png", roi_mask)

    overlay = image.copy()
    overlay[roi_mask > 0] = [0, 255, 255]
    cv2.imwrite(f"{folder_name}/05_overlay_roi_on_image.png", overlay)

    overlay_segments = overlay.copy()
    y_c, x_c = np.array(roi_mask.shape) // 2
    for i in range(72):
        theta1 = (i * 2 * pi / 72)
        r_outer = 200
        x1 = int(x_c + r_outer * np.cos(theta1))
        y1 = int(y_c + r_outer * np.sin(theta1))
        cv2.line(overlay_segments, (x_c, y_c), (x1, y1), (0, 0, 255), 1)
    cv2.imwrite(f"{folder_name}/06_overlay_72_segments.png", overlay_segments)
print(f"Min: {E_min:.2f}, Avg: {E_avg:.2f}, Max: {E_max:.2f}")
