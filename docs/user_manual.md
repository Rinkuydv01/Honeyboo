# HoneyBoo User Manual
### A Step-by-Step Guide for Beekeepers & Researchers

Welcome to **HoneyBoo**, an easy-to-use computer vision system for tracking honeybee entrance traffic. You do not need programming knowledge to operate HoneyBoo.

---

## Step 1: Open the Application
1. Start the application using `./scripts/run_all.sh` (or `scripts\run_all.bat` on Windows).
2. Open your web browser and navigate to:
   **`http://127.0.0.1:5173`** (or `http://127.0.0.1:8000`)
3. You will see the **HoneyBoo Dashboard**, presenting total incoming bees, outgoing bees, net drift, and recent activity alerts.

---

## Step 2: Upload a Hive Entrance Video
1. Click **"Upload & Setup"** in the top navigation bar.
2. Either:
   - Drag and drop your hive entrance video (`.mp4`, `.avi`, or `.mov`) into the upload box, OR
   - Click the box to browse and select a video file from your computer.
3. Click **"Upload & Prepare Video"**.
4. HoneyBoo will analyze the video, extract its duration and resolution, and capture a reference frame for entrance alignment.

---

## Step 3: Configure the Virtual Entrance Line
1. Once the video frame appears on the screen, notice the virtual entrance line with two circular handles labeled **P1** and **P2**.
2. **Align the Line:**
   - Click and drag **P1** to one end of your hive's physical entrance slot.
   - Click and drag **P2** to the opposite end of the entrance slot.
   - Use the **Quick Presets** (e.g. *Bottom Slot*, *Center Line*) if your camera is placed facing the standard landing board.
3. **Set Hive Interior Direction:**
   - Under *Hive Interior*, select which side represents the inside of your beehive: `Bottom`, `Top`, `Left`, or `Right`.
   - The green arrow on the canvas indicates the interior. Bees crossing in the direction of the green arrow will be counted as **INCOMING** (returning to hive). Bees crossing in the opposite direction will be counted as **OUTGOING** (departing).

---

## Step 4: Configure Detection Settings
Adjust the simple sliders according to your requirements:
- **Confidence Threshold (Default 25%):** How sure the vision model must be before considering an object as a bee.
- **Frame Skipping (Default 1x):** If your computer has a slower processor, set to `Every 2 frames` to speed up processing.
- **Crossing Cooldown (Default 25 frames):** Prevents counting bees that hover or walk back and forth along the entrance.
- **Simulation Mode Toggle:** Check this box if you are testing the interface with simulated sample detections without a custom-trained model.

Click **"Start Entrance Counting Pipeline"**.

---

## Step 5: Monitor Live Processing
The **Processing Page** displays:
- **Live Progress Bar:** Shows the percentage completed and current frame number.
- **Incoming Count (Green):** Count of bees that entered the hive.
- **Outgoing Count (Amber):** Count of bees that left the hive.
- **Net Movement (Blue):** Incoming minus outgoing.
- **Cancel Button:** Allows you to stop processing safely at any time.

---

## Step 6: Explore Activity Analytics & Graphs
When processing completes, click **"View Full Analytics"**:
- **Incoming vs Outgoing Line Graph:** Visualizes temporal foraging trends.
- **Total Entrance Traffic Bar Chart:** Shows total entrance traffic across 1-minute, 5-minute, or 15-minute windows.
- **Net Drift Area Graph:** Shows whether net bees are returning or leaving during each interval.
- **Annotated Video Player:** Watch the processed video with detected boxes, bee IDs, and real-time counter overlay. Click **"Download MP4"** to save a copy.
- **Individual Crossing Events Log:** An exact log of every recorded crossing with timestamps and confidence scores.

---

## Step 7: Review Anomaly Alerts
Click **"Alerts"** in the top navigation bar to inspect automated observations:
- **Low Activity Alert:** Triggered when entrance traffic drops significantly below the rolling baseline.
- **High Activity Alert:** Triggered during unexpected entrance rushes.
- **Sudden Drop:** Triggered when traffic abruptly collapses compared to the preceding minute.
- **Important Note:** Alerts describe traffic anomalies; they do not diagnose diseases. Combine alerts with physical hive inspections.

---

## Step 8: Manage Video History
Click **"History"** to view all uploaded videos. You can re-run detection with different line coordinates or delete old videos to save hard drive space.
