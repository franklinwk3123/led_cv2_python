
# LED 環形亮度均勻度分析與校正工具

這是一套針對 LED 環形光源的影像處理工具，提供兩大功能：

1. **均勻度分析**：將環狀 LED 平均分為 72 個區段，計算每段亮度。
2. **校正比對**：與 Golden 樣本 RGB 進行對比，產出每區段的 RGB 色差。

---

## 📁 專案檔案說明

| 檔案名稱 | 說明 |
|----------|------|
| `led_roi_utils.py`               | 共用函式庫：ROI 擷取、分段分析、影像儲存 |
| `uniformity.py`                 | 均勻度分析主程式，輸出 72 區段亮度與圖像 |
| `calibration.py`                | 與 Golden 圖片比對的校正工具（RGB 差異） |

---

## ▶️ 安裝套件

```bash
pip install opencv-python numpy pandas
```

---

## ✅ 使用方式

### 1. 進行亮度均勻度分析

```bash
python uniformity.py path/to/your_led_image.png
```

### 2. 執行 LED 校正與差異分析

```bash
python calibration.py path/to/golden_image.png path/to/dut_image.png
```

---

## 📂 分析與圖像輸出

每次執行會產生：

```
led_result_[圖片檔名]_YYYYMMDD/
├── 01_gray_image.png               # 原圖轉灰階
├── 02_threshold_mask.png           # Otsu 門檻後的遮罩
├── 03_contour_outline.png          # 擷取輪廓
├── 04_ring_roi_mask.png            # 內縮後的環狀 ROI
├── 05_overlay_roi_on_image.png     # 疊圖結果
├── uniformity.csv                  # 均勻度分析結果（若使用 uniformity.py）
├── calib_R.csv / G.csv / B.csv     # 各通道色差結果（若使用 calibration.py）
```

---

## 📈 統計指標

- 每段亮度（灰階平均）
- Uniformity \(U₀ = E_{min} / E_{avg}\)
- 每段 RGB 差異（DUT - Golden）

---

## ⚙️ 可調參數

| 參數 | 說明 |
|------|------|
| `thickness` | ROI 厚度（預設為 10） |
| `num_segments` | 分區數量，預設為 72 |

可於主程式或 `led_roi_utils.py` 中調整。

---

## 🧠 延伸應用建議

- 可結合相機 SDK（如 pypylon）即時擷取影像分析
- 可搭配 LUT 或 EEPROM 進行動態 LED 校正


---

## 📷 實時擷取支援：Basler pypylon

若您使用 Basler 工業相機進行實時 LED 擷取與分析，請先安裝：

```bash
pip install pypylon
```

使用範例架構：

```python
from pypylon import pylon
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
camera.StartGrabbing()
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_RGB8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
if grabResult.GrabSucceeded():
    image = converter.Convert(grabResult)
    img = image.GetArray()  # 可直接傳入 ROI 分析函式
```

👉 完整擷取後，可用 `segment_ring_roi()` 與 `get_ring_roi_from_contour()` 分析該影像，流程與靜態圖一致。
