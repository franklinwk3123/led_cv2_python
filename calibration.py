
import sys
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
from led_roi_utils import get_threshold_mask, get_largest_contour, get_ring_roi_from_contour, segment_ring_roi, save_process_images

if len(sys.argv) != 3:
    print("Usage: python calibration.py <golden_image> <dut_image>")
    exit(1)

golden_img = cv2.imread(sys.argv[1])
dut_img = cv2.imread(sys.argv[2])

assert golden_img.shape == dut_img.shape, "Golden 和 DUT 圖片必須具有相同解析度！"
gray_golden = cv2.cvtColor(golden_img, cv2.COLOR_BGR2GRAY)
mask = get_threshold_mask(gray_golden)
contour = get_largest_contour(mask)
roi_mask = get_ring_roi_from_contour(contour, gray_golden.shape, thickness=10)

# 建立資料夾
folder_name = f"led_result_{os.path.splitext(os.path.basename(sys.argv[2]))[0]}_{datetime.now().strftime('%Y%m%d')}"
os.makedirs(folder_name, exist_ok=True)

save_process_images(dut_img, cv2.cvtColor(dut_img, cv2.COLOR_BGR2GRAY), mask, contour, roi_mask, folder_name)

# RGB 差異分析
rgb_names = ['R', 'G', 'B']
result = []

for c, name in enumerate(rgb_names):
    golden_vals = segment_ring_roi(golden_img, roi_mask, channel=c)
    dut_vals = segment_ring_roi(dut_img, roi_mask, channel=c)
    diff = np.array(dut_vals) - np.array(golden_vals)
    result.append((name, golden_vals, dut_vals, diff.tolist()))

# 輸出到統一的資料夾
for name, gold, dut, diff in result:
    df = pd.DataFrame({
        "Segment": list(range(1, 73)),
        f"{name}_Golden": gold,
        f"{name}_DUT": dut,
        f"{name}_Diff": diff
    })
    df.to_csv(f"{folder_name}/calib_{name}.csv", index=False)

print("Calibration comparison saved.")
