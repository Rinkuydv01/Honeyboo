import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "HoneyBoo: Honeybee Hive Activity and Health Monitoring System")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 747, letter[0] - 54, 747)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_text)
        self.drawString(54, 32, "Confidential • Academic Project Complete Reference • CSE471")
        self.restoreState()

def build_pdf(filename="HoneyBoo_Project_Complete_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#B45309")     # Honey Amber Dark
    SECONDARY = colors.HexColor("#D97706")   # Honey Amber
    ACCENT = colors.HexColor("#059669")      # Emerald Green
    DARK = colors.HexColor("#0F172A")        # Dark Charcoal / Slate
    TEXT = colors.HexColor("#1E293B")        # Body text
    MUTED = colors.HexColor("#64748B")       # Subtitle text
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Card / Box background
    BORDER_LIGHT = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=MUTED,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=DARK,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    formula_style = ParagraphStyle(
        'Formula',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=9.5,
        leading=13,
        textColor=DARK,
        backColor=colors.HexColor("#FEF3C7"),
        borderColor=colors.HexColor("#FDE68A"),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#92400E"),
        backColor=colors.HexColor("#FEF9C3"),
        borderColor=colors.HexColor("#FACC15"),
        borderWidth=1,
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=10
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT
    )

    story = []

    # ==================== COVER / HEADER ====================
    story.append(Paragraph("HoneyBoo: Honeybee Hive Activity and Health Monitoring System", title_style))
    story.append(Paragraph("Complete Technical Project Reference Guide • Architecture, Machine Learning, Formulas & Workflows", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceBefore=0, spaceAfter=10))

    # Scientific Disclaimer Callout
    disclaimer_text = (
        "<b>IMPORTANT SCIENTIFIC LIMITATION:</b> HoneyBoo detects and counts honeybee entrance movements "
        "using optical computer vision. Entrance activity indicators reflect behavioral traffic patterns and "
        "<b>must not be interpreted as confirmed colony disease diagnoses or comprehensive colony health assessments</b>. "
        "Entrance traffic fluctuations should always be corroborated by physical hive inspections."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    # ==================== SECTION 1: WHAT IS THIS PROJECT ====================
    story.append(Paragraph("1. What is HoneyBoo?", h1_style))
    story.append(Paragraph(
        "<b>HoneyBoo</b> is an end-to-end, non-invasive computer vision system that monitors honeybee colonies by "
        "analyzing video recordings taken at the hive entrance. In traditional apiculture, checking a hive requires "
        "opening the wooden boxes, which disrupts brood temperature, stresses the queen, and makes worker bees defensive. "
        "HoneyBoo solves this problem by using standard video footage (from a smartphone or webcam) to automatically "
        "detect bees, track their flight paths, and count exactly how many bees are <b>entering</b> versus <b>exiting</b> "
        "the hive over time without ever opening the colony.",
        body_style
    ))
    story.append(Paragraph("<b>Primary Real-World Benefits:</b>", body_style))
    story.append(Paragraph("• <b>Zero-Touch Monitoring:</b> The beekeeper positions an ordinary smartphone or laptop camera facing the hive landing board.", bullet_style))
    story.append(Paragraph("• <b>Bidirectional Counting:</b> Distinguishes incoming returning nectar/pollen foragers from outgoing departing foragers.", bullet_style))
    story.append(Paragraph("• <b>Traffic Rhythms & Anomaly Indicators:</b> Identifies abnormal spikes or sudden activity drops that warrant inspection.", bullet_style))
    story.append(Paragraph("• <b>100% Free & Local:</b> Runs on a standard laptop without expensive cloud subscriptions, Raspberry Pi, or external electronics.", bullet_style))

    # ==================== SECTION 2: HOW IT WORKS ====================
    story.append(Paragraph("2. How HoneyBoo Works: The 10-Step Pipeline", h1_style))
    story.append(Paragraph(
        "The computer vision and data pipeline transforms raw optical video into actionable beekeeper insights:",
        body_style
    ))

    pipeline_steps = [
        ("Step 1: Video Ingestion", "User uploads an MP4, AVI, or MOV video. OpenCV decodes the video to verify duration, resolution, and frame rate."),
        ("Step 2: Low-Resource Rescaling", "To keep memory under 2GB VRAM, frames larger than 960px width are proportionally scaled down before inference."),
        ("Step 3: Object Detection", "A lightweight YOLO neural network scans each frame and detects bees, predicting bounding boxes and confidence scores."),
        ("Step 4: Multi-Object Tracking", "The ByteTrack algorithm assigns a unique ID (e.g. Bee #14) to each bee and tracks its centroid trajectory over consecutive frames."),
        ("Step 5: Virtual Entrance Line", "The user configures a virtual line across the entrance on an interactive web canvas and designates the hive interior side."),
        ("Step 6: Directional Crossing Math", "A vector cross-product formula checks if a bee's movement line intersects the entrance line, determining if it moved Inside or Outside."),
        ("Step 7: Anti-Duplication Cooldown", "Bees lingering or hovering near the line are prevented from triggering multiple counts using an ID-based frame cooldown window."),
        ("Step 8: Database Persistence", "Every valid crossing event is stored in an SQLite database with timestamp, frame number, track ID, and direction."),
        ("Step 9: Anomaly Detection", "The analytics engine calculates 1-min, 5-min, and 15-min intervals, rolling Z-score baselines, and sudden percentage drops."),
        ("Step 10: Dashboard & Annotated Video", "The React frontend displays live traffic charts, anomaly alerts, and an annotated output video with detected bounding boxes and HUD."),
    ]

    for step_title, step_desc in pipeline_steps:
        story.append(Paragraph(f"• <b>{step_title}:</b> {step_desc}", bullet_style))

    # ==================== SECTION 3: TECH STACK & JUSTIFICATION ====================
    story.append(PageBreak())
    story.append(Paragraph("3. Technology Stack & Why Each Was Chosen", h1_style))
    story.append(Paragraph(
        "Every technology in HoneyBoo was specifically selected to maximize local efficiency, eliminate third-party costs, "
        "and run comfortably on an Intel Core i5 with 8GB RAM and a 4GB GPU (or CPU fallback):",
        body_style
    ))

    tech_table_data = [
        [
            Paragraph("<b>Component</b>", table_header_style),
            Paragraph("<b>Technology</b>", table_header_style),
            Paragraph("<b>Why Chosen (Technical Justification)</b>", table_header_style)
        ],
        [
            Paragraph("<b>Computer Vision</b>", table_cell_style),
            Paragraph("OpenCV (cv2)", table_cell_style),
            Paragraph("Industry standard for fast frame extraction, video decoding, stream management, and drawing annotated HUD overlays.", table_cell_style)
        ],
        [
            Paragraph("<b>Deep Learning</b>", table_cell_style),
            Paragraph("PyTorch & Ultralytics", table_cell_style),
            Paragraph("Provides state-of-the-art YOLO inference, automatic CUDA/MPS/CPU hardware acceleration, and seamless model loading.", table_cell_style)
        ],
        [
            Paragraph("<b>Tracking Algorithm</b>", table_cell_style),
            Paragraph("ByteTrack", table_cell_style),
            Paragraph("Much lighter than DeepSORT. Re-associates occluded bees using low-confidence detections without requiring a heavy Re-ID neural net.", table_cell_style)
        ],
        [
            Paragraph("<b>Backend Web API</b>", table_cell_style),
            Paragraph("Python FastAPI", table_cell_style),
            Paragraph("High-performance asynchronous REST API framework with native Pydantic data validation and auto-generated Swagger UI (/docs).", table_cell_style)
        ],
        [
            Paragraph("<b>Database</b>", table_cell_style),
            Paragraph("SQLite + SQLAlchemy", table_cell_style),
            Paragraph("Zero-configuration, portable, file-based SQL database. Avoids setting up Docker, PostgreSQL, or Redis for simple local execution.", table_cell_style)
        ],
        [
            Paragraph("<b>Frontend Framework</b>", table_cell_style),
            Paragraph("React 18 + TypeScript", table_cell_style),
            Paragraph("Component-based reactive UI with strict type safety, ensuring instant updates during live video processing polling.", table_cell_style)
        ],
        [
            Paragraph("<b>Build Tooling</b>", table_cell_style),
            Paragraph("Vite", table_cell_style),
            Paragraph("Sub-second hot-module reloading and rapid production bundling (2s build time), dramatically faster than Webpack.", table_cell_style)
        ],
        [
            Paragraph("<b>Styling & Charts</b>", table_cell_style),
            Paragraph("Tailwind CSS + Recharts", table_cell_style),
            Paragraph("Tailwind enables a warm, honeybee-inspired dark theme; Recharts renders smooth, responsive SVG time-series graphs.", table_cell_style)
        ]
    ]

    tech_table = Table(tech_table_data, colWidths=[100, 110, 294])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(tech_table)

    # ==================== SECTION 4: AI MODELS & TRACKING ====================
    story.append(Paragraph("4. AI Models & Tracking Architecture", h1_style))
    story.append(Paragraph("<b>4.1 Why YOLOv8 Nano (YOLOv8n)?</b>", h2_style))
    story.append(Paragraph(
        "YOLOv8n is an ultra-lightweight convolutional neural network with only <b>3.2 million parameters</b> and an 8.7 GFLOP footprint. "
        "Unlike heavy models (YOLOv8x with 68M parameters), the Nano variant requires under 1.2 GB of GPU VRAM or runs at 20–30 FPS on "
        "a standard Intel Core i5 processor, perfectly honoring our zero-budget hardware constraints.",
        body_style
    ))

    story.append(Paragraph("<b>4.2 How ByteTrack Tracks Individual Bees</b>", h2_style))
    story.append(Paragraph(
        "In video recordings of a hive entrance, bees frequently overlap, fly past one another, or experience motion blur. "
        "Traditional trackers discard detections with confidence scores below 0.5. ByteTrack's key innovation is a <b>two-tier association</b>: "
        "<br/>1. It first matches high-confidence detections with active tracks using Intersection-over-Union (IoU). "
        "<br/>2. It then matches remaining unassigned tracks against <i>low-confidence</i> detections (e.g. partially occluded bees). "
        "This maintains track persistence through flight occlusions without allocating new false IDs.",
        body_style
    ))

    story.append(Paragraph("<b>4.3 Model Discovery & Test Simulation Fallback</b>", h2_style))
    story.append(Paragraph(
        "HoneyBoo inspects the <code>models/</code> folder on startup. If a custom bee weight file (<code>yolov8n_bee.pt</code>) is found, "
        "it is loaded automatically. If absent, HoneyBoo checks for a local base model. If no local weights exist, HoneyBoo automatically "
        "switches to an explicitly labeled simulation test mode. This prevents unexpected network download failures and ensures "
        "the application runs offline immediately upon installation.",
        body_style
    ))

    # ==================== SECTION 5: MATHEMATICAL FORMULAS ====================
    story.append(PageBreak())
    story.append(Paragraph("5. Formulas & Mathematical Logic (Explained Simply)", h1_style))
    story.append(Paragraph(
        "Behind HoneyBoo's clean interface lies rigorous 2D vector geometry and statistics. Here are the core mathematical formulas:",
        body_style
    ))

    # Formula 1
    story.append(Paragraph("Formula 1: Signed 2D Cross-Product Distance (Line Side Check)", h2_style))
    story.append(Paragraph(
        "To determine whether a bee at position P(x, y) is on the outside or inside of virtual line segment A(x1, y1) → B(x2, y2), "
        "we compute the 2D cross-product (the determinant):",
        body_style
    ))
    story.append(Paragraph("S(P) = (B.x - A.x) * (P.y - A.y) - (B.y - A.y) * (P.x - A.x)", formula_style))
    story.append(Paragraph(
        "<b>In Simple Words:</b><br/>"
        "• If S(P) > 0, the bee is on one side of the entrance line.<br/>"
        "• If S(P) < 0, the bee is on the opposite side.<br/>"
        "• If S(P_prev) has a different sign than S(P_curr), the bee has <b>crossed the line threshold</b>!",
        body_style
    ))

    # Formula 2
    story.append(Paragraph("Formula 2: Parametric Segment Intersection (No Boundary Leakage)", h2_style))
    story.append(Paragraph(
        "To ensure a bee didn't just fly around the line in empty space, we verify that the line segment from P_prev to P_curr "
        "physically intersects line segment AB using counter-clockwise orientation checks (ccw):",
        body_style
    ))
    story.append(Paragraph(
        "ccw(A, B, C) = (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)<br/>"
        "Intersect = [sign(ccw(A,B,P_prev)) != sign(ccw(A,B,P_curr))] AND [sign(ccw(P_prev,P_curr,A)) != sign(ccw(P_prev,P_curr,B))]",
        formula_style
    ))
    story.append(Paragraph(
        "<b>In Simple Words:</b> Guarantees the bee's flight line actually cuts directly across the virtual gate.",
        body_style
    ))

    # Formula 3
    story.append(Paragraph("Formula 3: Direction Classification (Incoming vs Outgoing)", h2_style))
    story.append(Paragraph(
        "We place an interior reference probe point P_probe offset toward the configured hive interior direction (e.g. +y for bottom).<br/>"
        "Let InsideSign = sign(S(P_probe)).<br/>"
        "• <b>INCOMING:</b> sign(S(P_prev)) != InsideSign AND sign(S(P_curr)) == InsideSign (Bee moved from outside into hive).<br/>"
        "• <b>OUTGOING:</b> sign(S(P_prev)) == InsideSign AND sign(S(P_curr)) != InsideSign (Bee moved from inside to outside).",
        body_style
    ))

    # Formula 4
    story.append(Paragraph("Formula 4: Net Traffic Drift & Incoming-to-Outgoing Ratio", h2_style))
    story.append(Paragraph(
        "Net Movement = Total Incoming - Total Outgoing<br/>"
        "Traffic Ratio = Total Incoming / Total Outgoing (when Outgoing > 0)",
        formula_style
    ))
    story.append(Paragraph(
        "<b>In Simple Words:</b> A positive Net Drift means foragers are returning home with food; a negative Net Drift indicates a foraging departure wave. "
        "<i>Note: Net movement is an optical entrance count, not a total count of bees inside the hive!</i>",
        body_style
    ))

    # Formula 5
    story.append(Paragraph("Formula 5: Statistical Anomaly Detection (Rolling Z-Score)", h2_style))
    story.append(Paragraph(
        "To identify unusually high or low activity without hardcoding arbitrary thresholds, HoneyBoo calculates the rolling mean (μ) "
        "and rolling standard deviation (σ) across the previous 5 intervals:",
        body_style
    ))
    story.append(Paragraph(
        "Z = (Current_Activity - μ) / σ<br/>"
        "If Z >= +2.0  --> Triggers 'HIGH_ACTIVITY' alert<br/>"
        "If Z <= -2.0  --> Triggers 'LOW_ACTIVITY' alert",
        formula_style
    ))

    # Formula 6
    story.append(Paragraph("Formula 6: Sudden Percentage Drop Rate", h2_style))
    story.append(Paragraph(
        "Delta = (Previous_Activity - Current_Activity) / Previous_Activity<br/>"
        "If Delta >= 0.60 (60% abrupt collapse in traffic) --> Triggers 'SUDDEN_DROP' warning",
        formula_style
    ))

    # ==================== SECTION 6: WEB DASHBOARD MODULES ====================
    story.append(PageBreak())
    story.append(Paragraph("6. Web Dashboard Modules", h1_style))
    story.append(Paragraph(
        "The HoneyBoo dashboard provides 7 cohesive pages designed for effortless navigation:",
        body_style
    ))

    dashboard_modules = [
        ("Dashboard Home", "Displays cumulative metric cards (Incoming, Outgoing, Total, Net Drift), the latest session badge, and recent alerts. Features a clean empty state when no recordings exist."),
        ("Upload & Setup", "Allows drag-and-drop video uploads, displays video resolution/duration metadata, and embeds the interactive HTML5 canvas to align line handles P1 and P2."),
        ("Processing Monitor", "Displays real-time frame progress (0-100%), live incoming/outgoing counter increments, and a safe one-click cancellation button."),
        ("Activity Analytics", "Presents time-series line charts (Incoming vs Outgoing), total traffic bar charts, net movement area charts, an annotated MP4 video player, and a raw crossing event log."),
        ("Alerts & Monitoring", "Aggregates statistical anomaly alerts (high traffic, low traffic, sudden drop) with baseline numbers, plain-English explanations, and mandatory scientific disclaimers."),
        ("Video History", "Archives uploaded videos with duration and resolution, allowing users to re-run detection with different line coordinates or delete files cleanly."),
        ("Settings & Hardware", "Displays active hardware compute capabilities (CPU / CUDA / MPS), default detection confidence, frame skipping, and model weight discovery status."),
    ]

    for mod_title, mod_desc in dashboard_modules:
        story.append(Paragraph(f"• <b>{mod_title}:</b> {mod_desc}", bullet_style))

    # ==================== SECTION 7: LOW-RESOURCE OPTIMIZATION ====================
    story.append(Paragraph("7. Hardware & Zero-Budget Optimization", h1_style))
    story.append(Paragraph(
        "HoneyBoo achieves smooth local execution through four architectural techniques:",
        body_style
    ))
    story.append(Paragraph("1. <b>Dynamic Downscaling:</b> High-resolution videos are rescaled to 960px width before entering the neural network, keeping VRAM under 1.5 GB.", bullet_style))
    story.append(Paragraph("2. <b>Sequential Stream Processing:</b> OpenCV reads frames one-by-one from disk and releases them immediately. Entire videos are never buffered into RAM.", bullet_style))
    story.append(Paragraph("3. <b>Configurable Frame Skipping:</b> Processing every 2nd or 3rd frame cuts computational load in half while ByteTrack smoothly bridges the trajectory gap.", bullet_style))
    story.append(Paragraph("4. <b>Automatic Device Fallback:</b> PyTorch detects whether an NVIDIA GPU (CUDA), Apple Silicon GPU (MPS), or CPU is present, executing without manual driver configuration.", bullet_style))

    # ==================== SECTION 8: VIVA CHEAT SHEET ====================
    story.append(Paragraph("8. Project Viva / Defense Quick Cheat Sheet", h1_style))
    story.append(Paragraph(
        "Common questions evaluators or professors ask during project evaluations:",
        body_style
    ))

    viva_qa = [
        ("Why not count bees using background subtraction or optical flow?",
         "Background subtraction fails because the hive landing board suffers from fluctuating sunlight, shadows, and crawling bees that stop moving. YOLO learns visual morphological features (wings, stripes) regardless of lighting."),
        ("How does HoneyBoo prevent counting a lingering bee ten times?",
         "Through three layers of protection: (1) ByteTrack persistent track IDs, (2) a configurable frame cooldown (N >= 25 frames) per bee ID, and (3) requiring at least 3 historical trajectory points before registering a crossing."),
        ("Why does the system refuse to diagnose colony diseases from entrance video?",
         "It is a core scientific limitation. Foraging traffic fluctuates naturally due to clouds, temperature, wind, and nectar availability. A decline in traffic can indicate rain or cold, not necessarily foulbrood or mites. Overpromising medical diagnoses from video alone is scientifically irresponsible."),
        ("What is the difference between Net Movement and Total Colony Population?",
         "Net Movement is strictly an entrance traffic flow observation (Incoming minus Outgoing during the video clip). It does not represent the thousands of bees resting or nursing brood inside the dark hive comb.")
    ]

    for q, a in viva_qa:
        story.append(Paragraph(f"<b>Q: {q}</b>", ParagraphStyle('Q', parent=body_style, fontName='Helvetica-Bold', textColor=PRIMARY, spaceBefore=4)))
        story.append(Paragraph(f"<b>A:</b> {a}", ParagraphStyle('A', parent=body_style, spaceAfter=6)))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF documentation at: {filename}")

if __name__ == "__main__":
    out_pdf = "HoneyBoo_Project_Complete_Guide.pdf"
    build_pdf(out_pdf)
