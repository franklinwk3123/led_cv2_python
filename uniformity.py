
import sys
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime
from led_roi_utils import get_threshold_mask, get_largest_contour, get_ring_roi_from_contour, segment_ring_roi, save_process_images

if len(sys.argv) != 2:
    print("Usage: python uniformity.py <image>")
    exit(1)

image_path = sys.argv[1]
image = cv2.imread(image_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
mask = get_threshold_mask(gray)
contour = get_largest_contour(mask)
roi_mask = get_ring_roi_from_contour(contour, gray.shape, thickness=10)
brightness = segment_ring_roi(gray, roi_mask, num_segments=72)

folder_name = f"led_result_{os.path.splitext(os.path.basename(image_path))[0]}_{datetime.now().strftime('%Y%m%d')}"
save_process_images(image, gray, mask, contour, roi_mask, folder_name)

df = pd.DataFrame({"Segment": list(range(1, 73)), "Brightness": brightness})
df.to_csv(f"{folder_name}/uniformity.csv", index=False)

print("Uniformity analysis done.")
