# HoneyBoo Local Storage Directory

This directory stores uploaded video files, generated annotated videos, frame previews, and the SQLite database.

## Subdirectories
- `uploads/`: Stores raw user-uploaded MP4, AVI, and MOV video files.
- `processed/`: Stores generated annotated output videos (`annotated_<session_id>.mp4`) with bounding boxes, tracking IDs, and real-time HUD overlays.
- `honeyboo.db`: The local SQLite database storing video metadata, sessions, crossing events, and anomaly alerts.
