# HoneyBoo: Custom Honeybee Detection Model Training Guide

This guide provides step-by-step instructions for training a custom YOLOv8 model specifically for honeybee detection at hive entrances.

---

## 1. Why a Bee-Specific Model is Required

Generic pretrained object detection models (such as COCO-pretrained YOLOv8) are trained on 80 broad common categories (people, cars, dogs, bottles). They do not contain a "honeybee" category:
- Small object scale: Honeybees typically occupy between $15 \times 15$ to $60 \times 60$ pixels in entrance recordings.
- Rapid wing motion and flight blur require bee-specific visual features.
- A custom-trained model trained on annotated honeybee entrance footage achieves $\ge 90\%$ mAP@50, compared to erratic detections with generic models.

---

## 2. Dataset Collection & Video Annotation

### 2.1 Video Recording Guidelines
- Mount camera 30–60 cm from the hive landing board.
- Avoid camera vibration by using a mini tripod or clamp.
- Record at 25 or 30 FPS under good natural daylight.

### 2.2 Recommended Annotation Tools
- **Roboflow (Free Tier):** Excellent web-based tool for drawing bounding boxes and exporting in YOLOv8 format.
- **CVAT (Computer Vision Annotation Tool):** Free, open-source tool for frame-by-frame video annotation.
- **LabelImg:** Lightweight desktop annotation software.

### 2.3 Labeling Rules
- Label the visible body of every bee (including legs and head).
- Only 1 class name: `bee` (Class ID `0`).
- Ensure bounding boxes tightly enclose the bee body.

---

## 3. YOLO Dataset Directory Structure

Organize your dataset in a folder named `bee_dataset/`:

```
bee_dataset/
├── data.yaml
├── train/
│   ├── images/
│   │   ├── frame_001.jpg
│   │   └── ...
│   └── labels/
│       ├── frame_001.txt
│       └── ...
└── val/
    ├── images/
    │   ├── frame_100.jpg
    │   └── ...
    └── labels/
        ├── frame_100.txt
        └── ...
```

### `data.yaml` Configuration File
Create `bee_dataset/data.yaml`:

```yaml
path: /path/to/bee_dataset
train: train/images
val: val/images

nc: 1
names: ['bee']
```

Each label `.txt` file contains one line per bee:
```
<class_id> <x_center> <y_center> <width> <height>
0 0.4521 0.6312 0.0450 0.0380
```
*(All coordinates normalized between 0.0 and 1.0).*

---

## 4. Training on Low-Resource Hardware (GTX 1650 / 4GB VRAM)

To train on an Intel Core i5 with a 4GB NVIDIA GTX 1650 or CPU:
- Model architecture: `yolov8n.pt` (Nano - only 3.2 million parameters).
- Image size: `640`
- Batch size: `16` (or `8` if VRAM is constrained).
- Epochs: `50` to `100`

### Training Command (Terminal / CLI)
Run inside the HoneyBoo backend virtual environment:

```bash
# Activate backend environment
source backend/venv/bin/activate  # On Linux/macOS
# or: backend\venv\Scripts\activate  # On Windows

# Start training
yolo detect train \
  data=bee_dataset/data.yaml \
  model=yolov8n.pt \
  epochs=60 \
  imgsz=640 \
  batch=16 \
  device=0 \
  project=runs/bee_training \
  name=honeybee_model
```
*(If training on CPU, replace `device=0` with `device=cpu` and set `batch=8`).*

### Training via Python Script
Alternatively, create a temporary training script:

```python
from ultralytics import YOLO

# Load lightweight base model
model = YOLO('yolov8n.pt')

# Train on custom bee dataset
results = model.train(
    data='bee_dataset/data.yaml',
    epochs=60,
    imgsz=640,
    batch=16,
    device=0,  # Or 'cpu'
    workers=2,
    name='honeybee_model'
)
```

---

## 5. Model Validation

Evaluate the trained model on validation frames:

```bash
yolo detect val \
  model=runs/bee_training/honeybee_model/weights/best.pt \
  data=bee_dataset/data.yaml \
  imgsz=640
```
Target metrics:
- Precision $\ge 0.88$
- Recall $\ge 0.85$
- mAP50 $\ge 0.90$

---

## 6. Installing Trained Weights into HoneyBoo

1. Once training finishes, your optimal model weights will be saved at:
   `runs/bee_training/honeybee_model/weights/best.pt`
2. Copy this file into the HoneyBoo `models/` directory and rename it to `yolov8n_bee.pt`:

```bash
# Copy and rename to default model location
cp runs/bee_training/honeybee_model/weights/best.pt models/yolov8n_bee.pt
```

3. Restart the HoneyBoo backend server:
   - HoneyBoo will automatically discover `models/yolov8n_bee.pt`.
   - The dashboard Settings page and health endpoint will report:
     `Active Model: Custom Honeybee YOLO`.
   - Video processing sessions will now run with your custom-trained bee weights.
