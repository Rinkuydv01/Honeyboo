import math
import numpy as np
import cv2
from pathlib import Path

def generate_synthetic_hive_video(output_path: str, duration_sec: int = 8, fps: int = 25):
    """
    Generates a realistic synthetic hive entrance video for testing and offline development.
    Resolution: 640x360, containing a wooden hive landing board and simulated honeybees.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    width, height = 640, 360
    total_frames = duration_sec * fps

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (width, height))

    np.random.seed(42)

    # Bee parameters: (start_t, direction, x_start, speed)
    # direction: "IN" (starts y=30, moves to y=330) or "OUT" (starts y=330, moves to y=30)
    bees = [
        {"start_frame": 10, "dir": "IN", "x_base": 240, "speed": 4.5, "wobble": 25},
        {"start_frame": 35, "dir": "OUT", "x_base": 380, "speed": 5.0, "wobble": 30},
        {"start_frame": 60, "dir": "IN", "x_base": 300, "speed": 4.0, "wobble": 20},
        {"start_frame": 80, "dir": "OUT", "x_base": 420, "speed": 5.2, "wobble": 35},
        {"start_frame": 120, "dir": "IN", "x_base": 200, "speed": 4.8, "wobble": 25},
        {"start_frame": 140, "dir": "OUT", "x_base": 340, "speed": 4.6, "wobble": 20},
        {"start_frame": 170, "dir": "HOVER", "x_base": 280, "speed": 0.5, "wobble": 15},
    ]

    for f in range(total_frames):
        # 1. Base Hive Background: wooden texture landing board
        frame = np.full((height, width, 3), (120, 160, 190), dtype=np.uint8)  # Wood warm tone BGR

        # Hive entrance slot at bottom (y: 280 to 360)
        cv2.rectangle(frame, (0, 270), (width, 360), (45, 60, 75), -1)  # Dark hive interior
        cv2.line(frame, (0, 270), (width, 270), (20, 30, 40), 3)  # Entrance slot threshold

        # Landing board wood grain lines
        for y_line in [70, 130, 190, 250]:
            cv2.line(frame, (0, y_line), (width, y_line), (105, 145, 175), 1)

        # 2. Render moving bees
        for b in bees:
            if f < b["start_frame"]:
                continue
            age = f - b["start_frame"]
            
            if b["dir"] == "IN":
                y = 40 + age * b["speed"]
                x = b["x_base"] + math.sin(age * 0.15) * b["wobble"]
                if y > 350:
                    continue
            elif b["dir"] == "OUT":
                y = 310 - age * b["speed"]
                x = b["x_base"] + math.cos(age * 0.15) * b["wobble"]
                if y < 20:
                    continue
            else:  # HOVER near line
                y = 230 + math.sin(age * 0.08) * 20
                x = b["x_base"] + math.cos(age * 0.08) * 30

            bx, by = int(x), int(y)
            if 15 <= bx < width - 15 and 15 <= by < height - 15:
                # Bee body: amber-striped oval
                cv2.ellipse(frame, (bx, by), (14, 8), 25 * math.sin(age * 0.2), 0, 360, (15, 150, 230), -1)
                # Black stripes
                cv2.line(frame, (bx - 4, by - 6), (bx - 4, by + 6), (10, 10, 10), 2)
                cv2.line(frame, (bx + 2, by - 6), (bx + 2, by + 6), (10, 10, 10), 2)
                # Translucent wings
                wing_angle = math.sin(f * 1.5) * 40
                cv2.ellipse(frame, (bx - 2, by - 7), (10, 4), -30 + wing_angle, 0, 360, (230, 240, 255), 1)
                cv2.ellipse(frame, (bx - 2, by + 7), (10, 4), 30 - wing_angle, 0, 360, (230, 240, 255), 1)

        writer.write(frame)

    writer.release()
    return output_path

if __name__ == "__main__":
    out = "sample_videos/entrance_sample.mp4"
    generate_synthetic_hive_video(out)
    print(f"Generated synthetic video at {out}")
