
import sys
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import led_roi_utils as roi

if len(sys.argv) != 2:
    print("Usage: python uniformity.py <image>")
    exit(1)

image_path = sys.argv[1]
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# mask = roi.get_threshold_mask(gray, False, 250)
mask = roi.get_threshold_mask(gray)
if mask is None:
    print("No mask found. Please check the image.")
    exit(1)

use_thickness = False
if use_thickness:
    contour = roi.get_largest_contour(mask)
    roi_mask = roi.get_ring_roi_from_contour(contour, gray.shape, thickness=30)
    brightness = roi.segment_ring_gray_roi(gray, roi_mask, num_segments=72)
else:
    brightness = roi.segment_ring_gray_roi(gray, mask, num_segments=72)

folder_name = f"led_result_{os.path.splitext(os.path.basename(image_path))[0]}_{datetime.now().strftime('%Y%m%d')}"
roi.save_process_images(image, gray, mask, contour, roi_mask, folder_name)


min_brightness = np.min(brightness)
avg_brightness = np.mean(brightness)
uniformity_ratio = min_brightness / avg_brightness if avg_brightness > 0 else 0
pass_fail = "PASS" if uniformity_ratio >= 0.7 else "FAIL"
print(f"Uniformity = {uniformity_ratio:.3f} → {pass_fail}")
df = pd.DataFrame({"Segment": list(range(1, 73)), "Brightness": brightness})

# 將判斷結果加入最後一列
df.loc["Summary"] = [""] + [""] * (len(df.columns) - 2) + [pass_fail]
df.to_csv(f"{folder_name}/uniformity.csv", index=False)

print("Uniformity analysis done.")
