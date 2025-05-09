
import sys
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
import led_roi_utils as roi

if len(sys.argv) != 3:
    print("Usage: python calibration.py <golden_image> <dut_image>")
    exit(1)

golden_img = cv2.imread(sys.argv[1])
dut_img = cv2.imread(sys.argv[2])

assert golden_img.shape == dut_img.shape, "Golden 和 DUT 圖片必須具有相同解析度！"

gray_golden = cv2.cvtColor(golden_img, cv2.COLOR_BGR2GRAY)
mask = roi.get_threshold_mask(gray_golden)
contour = roi.get_largest_contour(mask)
roi_mask = roi.get_ring_roi_from_contour(contour, gray_golden.shape, thickness=30)

folder_name = f"led_result_{os.path.splitext(os.path.basename(sys.argv[2]))[0]}_{datetime.now().strftime('%Y%m%d')}"
os.makedirs(folder_name, exist_ok=True)
roi.save_process_images(golden_img, gray_golden, mask, contour, roi_mask, folder_name)

rgb_names = ['B', 'G', 'R']
result = []

for c, name in enumerate(rgb_names):
    golden_vals = roi.segment_ring_rgb_roi(golden_img, roi_mask, channel=c)
    dut_vals = roi.segment_ring_rgb_roi(dut_img, roi_mask, channel=c)
    diff = np.array(dut_vals) - np.array(golden_vals)
    result.append((name, golden_vals, dut_vals, diff.tolist()))

for name, gold, dut, diff in result:
    df = pd.DataFrame({
        "Segment": list(range(1, 73)),
        f"{name}_Golden": gold,
        f"{name}_DUT": dut,
        f"{name}_Diff": diff
    })
    df.to_csv(f"{folder_name}/calib_{name}.csv", index=False)

print("Calibration comparison saved.")
