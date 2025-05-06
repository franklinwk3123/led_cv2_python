import cv2
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi, cos, sin

# 這段程式碼是用來計算 LED 均勻度的，
# 主要步驟包括讀取圖片、轉換為灰階、應用閾值處理和計算均勻度。

threshold_value = 250 # 閾值，過濾光暈用

def load_image(path):
    image = cv2.imread(path)
    if image is None:
        raise ValueError("Image not found or unreadable.")
    return image

def convert_to_gray(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_threshold(gray_img, threshold_value):
    _, mask = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
    return mask

def get_countours(mask):
    # === 找到輪廓 ===
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        print("⚠️ 未偵測到亮點區域（請確認閾值是否正確）")
        return None
    else:
        # 取出最大的輪廓
        max_contour = max(contours, key=cv2.contourArea)
        return max_contour

def get_ring_roi_from_contour(contour, image_shape, thickness=10):
    # 建立原始輪廓遮罩
    mask_outer = np.zeros(image_shape, dtype=np.uint8)
    cv2.drawContours(mask_outer, [contour], -1, 255, -1)  # 填滿白色

    # 侵蝕輪廓建立內圈
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
    mask_inner = cv2.erode(mask_outer, kernel, iterations=1)

    # 建立環狀 ROI 遮罩
    ring_roi = cv2.subtract(mask_outer, mask_inner)
    return ring_roi

def draw_contours(image, mask):
    # === 畫出輪廓 ===
    contours = get_countours(mask)
    if contours is not None:
        cv2.drawContours(image, [contours], -1, (0, 255, 0), 3)
        roi_mask = get_ring_roi_from_contour(contours, gray.shape, thickness=10)

        # 可視化
        cv2.imshow("Ring ROI", roi_mask)

        # 接著就可以從 gray[roi_mask > 0] 擷取亮度做統計了
        roi_pixels = gray[roi_mask > 0]
        if roi_pixels.size > 0:
            print(f"Ring ROI Avg Brightness: {np.mean(roi_pixels):.2f}")
    else:
        print("⚠️ 無法畫出輪廓，請檢查圖片或閾值設定。")

def calculate_uniformity(mask):
    # === 從亮區中取出所有亮度值 ===
    bright_pixels = gray[mask > 0]
    if bright_pixels.size > 0:
        min_val = np.min(bright_pixels)
        max_val = np.max(bright_pixels)
        uniformity = min_val / max_val if max_val > 0 else 0
        print(f"Min: {min_val}, Max: {max_val}, Uniformity: {uniformity * 100:.2f}%")
    else:
        print("⚠️ 未偵測到亮點區域（請確認閾值是否正確）")

# --- 主流程 ---
if __name__ == "__main__":
    # === 設定參數 ===
    if len(sys.argv) != 2:
        print("⚠️ 使用方式: python test.py <圖片路徑>")
        exit(1)

    img_path = sys.argv[1]

    # === 讀取圖片（模擬擷取影像）===
    image = load_image(img_path)

    # === 轉灰階圖（模擬 demosaic + 灰階）===
    gray = convert_to_gray(image)

    # === 閾值處理，抓出亮區 ===
    mask = apply_threshold(gray, threshold_value)

    # === 計算均勻度 ===
    # calculate_uniformity(mask)
    draw_contours(image, mask)

    # === 顯示原圖與遮罩 ===
    # cv2.imshow("Original", image)
    # cv2.imshow("Gray", gray)
    # cv2.imshow("Threshold Mask", mask)
    print("ℹ️ 在視窗區塊內按下 'q' 鍵以關閉所有視窗")
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
