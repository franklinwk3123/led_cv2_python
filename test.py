import cv2
import numpy as np
import sys

# === 設定參數 ===
if len(sys.argv) != 2:
    print("⚠️ 使用方式: python test.py <圖片路徑>")
    exit(1)

img_path = sys.argv[1]
threshold_value = 50        # 閾值，過濾光暈用


# === 讀取圖片（模擬擷取影像）===
image = cv2.imread(img_path)
if image is None:
    print("⚠️ 無法讀取圖片，請檢查路徑是否正確。")
    exit(1)

# === 轉灰階圖（模擬 demosaic + 灰階）===
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# === 閾值處理，抓出亮區 ===
_, mask = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)

# === 從亮區中取出所有亮度值 ===
bright_pixels = gray[mask > 0]

if bright_pixels.size > 0:
    min_val = np.min(bright_pixels)
    max_val = np.max(bright_pixels)
    uniformity = min_val / max_val if max_val > 0 else 0

    print(f"Min: {min_val}, Max: {max_val}, Uniformity: {uniformity * 100:.2f}%")

else:
    print("⚠️ 未偵測到亮點區域（請確認閾值是否正確）")

# === 顯示原圖與遮罩 ===
cv2.imshow("Original", image)
cv2.imshow("Gray", gray)
cv2.imshow("Threshold Mask", mask)
print("ℹ️ 在視窗區塊內按下 'q' 鍵以關閉所有視窗")
while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()

