# HoneyBoo Models Directory

Place custom-trained YOLO honeybee detection weights in this directory.

## Default Model Location
- **Target File:** `yolov8n_bee.pt`
- **Fallback Base:** `yolov8n.pt`

## Behavior
1. If `models/yolov8n_bee.pt` is present, HoneyBoo loads it on startup as a high-confidence custom honeybee model.
2. If absent, HoneyBoo checks for a local `yolov8n.pt` base model.
3. If no weights are present, HoneyBoo runs in an explicitly labeled simulation test mode with clear user warnings.

See `docs/training_guide.md` for a complete guide on annotating bee footage and training custom YOLO weights.
