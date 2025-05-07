
# LED 環形均勻度分析工具

這個工具是用來分析 LED 環形發光模組的亮度分布情況，透過影像處理判斷是否均勻發光，並產出分析報告與每個處理步驟的對應圖檔。

---

## 📦 檔案說明

| 檔案名稱 | 說明 |
|----------|------|
| `led_uniformity_segmented_with_images.py` | 主程式，進行 LED 亮度分布分析 |
| `led_result_YYYYMMDD/` | 執行時自動產生的分析資料夾（依照日期命名） |
| `led_roi_brightness.csv` | 分析結果，包含 72 區段的平均亮度與統計 |

---

## ▶️ 使用方式

### 1. 安裝必要套件：

```bash
pip install opencv-python numpy pandas
```

### 2. 執行程式：

```bash
python led_uniformity_segmented_with_images.py path/to/your_led_image.png
```

請將 `path/to/your_led_image.png` 換成你的圖片路徑。

---

## 📂 執行輸出說明

執行完成後，會在本機產生如下資料夾與內容：

```
led_result_YYYYMMDD/
├── 01_gray_image.png               # 轉為灰階的原圖
├── 02_threshold_mask.png           # 自動 threshold 後的亮部遮罩
├── 03_contour_outline.png          # 找出的最大輪廓
├── 04_ring_roi_mask.png            # 環狀 ROI 遮罩
├── 05_overlay_roi_on_image.png     # 原圖疊加 ROI 區域
├── 06_overlay_72_segments.png      # 疊加 72 區段分割線
├── led_roi_brightness.csv          # 各角度平均亮度資料表
```

---

## 📊 分析輸出

終端機會輸出每段亮度資料與下列統計指標：

- `Uniformity (U₀)`：E_min / E_avg
- `Standard Deviation`
- `Min / Avg / Max` 亮度

---

## 🛠️ 調整參數

- **ROI 厚度** 可修改程式中 `get_ring_roi_from_contour()` 呼叫的 `thickness=100`
- **區段數量** 預設為 72，可改 `segment_ring_roi(gray, roi_mask, num_segments=72)`

---

## 📩 作者建議

此工具適用於具明顯環狀 LED 結構的影像，如需處理多圈、非中心對稱圖像，請聯絡作者以擴充功能。
