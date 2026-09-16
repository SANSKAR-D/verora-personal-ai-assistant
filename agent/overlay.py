import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QRadialGradient, QLinearGradient,
    QPainterPath, QFont, QPen, QBrush
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store


# ──────────────────────────────────────────────
#  Particle-stream Orb Widget
# ──────────────────────────────────────────────
class HoloOrb(QWidget):
    """
    Renders an animated particle-stream orb:
    - Dark charcoal sphere base
    - Multiple sinusoidal ribbon streams in cyan/teal
    - Depth (z) drives per-segment opacity → 3-D feel
    - Triple-pass draw per segment: wide soft glow + mid glow + bright core
    - Outer rim glow halo
    """

    # Stream configs: (tilt_y, tilt_x, speed, frequency, amplitude, phase_offset)
    _STREAMS = [
        (0.0,   0.0,  0.42, 2.0, 0.75, 0.00),
        (1.05,  0.3,  0.35, 2.5, 0.65, 1.30),
        (2.10,  0.6,  0.55, 1.8, 0.80, 2.60),
        (-0.55, 0.9,  0.28, 3.0, 0.55, 0.85),
        (3.30,  0.2,  0.48, 2.2, 0.70, 4.10),
    ]
    _N_SEG = 280   # segments per stream

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self._time = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    def _tick(self):
        self._time += 0.018
        self.update()

    # ── geometry ─────────────────────────────

    def _stream_pts(self, tilt_y, tilt_x, speed, freq, amp, phase_off, r):
        """Return list of (sx, sy, z_depth) for one stream."""
        phase = phase_off + self._time * speed
        pts = []
        n = self._N_SEG
        for i in range(n + 1):
            t = (i / n) * 2 * math.pi
            wave    = amp * math.sin(freq * t + phase)
            phi     = math.pi / 2 + wave          # latitude
            theta   = t                            # longitude

            # Sphere surface in local frame
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)

            # Rotate around Y axis (tilt_y)
            cy_t, sy_t = math.cos(tilt_y), math.sin(tilt_y)
            xr =  x * cy_t + z * sy_t
            yr =  y
            zr = -x * sy_t + z * cy_t

            # Rotate around X axis (tilt_x)
            cx_t, sx_t = math.cos(tilt_x), math.sin(tilt_x)
            xrr = xr
            yrr = yr * cx_t - zr * sx_t
            zrr = yr * sx_t + zr * cx_t

            pts.append((xrr * r, yrr * r, zrr))   # zrr in [-1, 1]
        return pts

    # ── paint ─────────────────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        r = 68.0

        # ── 1. Background sphere ──
        bg = QRadialGradient(QPointF(cx, cy), r)
        bg.setColorAt(0.0, QColor(50, 58, 68))
        bg.setColorAt(0.6, QColor(36, 42, 52))
        bg.setColorAt(1.0, QColor(20, 24, 32))
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), r, r)

        # ── 2. Clip to sphere ──
        clip = QPainterPath()
        clip.addEllipse(QPointF(cx, cy), r, r)
        p.setClipPath(clip)

        # ── 3. Particle streams ──
        for cfg in self._STREAMS:
            pts = self._stream_pts(*cfg, r=r)
            for i in range(len(pts) - 1):
                x1, y1, z1 = pts[i]
                x2, y2, z2 = pts[i + 1]

                # Depth → opacity (front bright, back dim)
                depth = (z1 + 1.0) * 0.5           # 0..1
                base_alpha = int(30 + depth * 195)

                sx1, sy1 = cx + x1, cy + y1
                sx2, sy2 = cx + x2, cy + y2

                pt1 = QPointF(sx1, sy1)
                pt2 = QPointF(sx2, sy2)

                # Pass 1 – wide soft outer glow
                pen = QPen(QColor(0, 210, 235, int(base_alpha * 0.30)))
                pen.setWidthF(6.0)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setPen(pen)
                p.drawLine(pt1, pt2)

                # Pass 2 – mid glow
                pen2 = QPen(QColor(30, 230, 250, int(base_alpha * 0.60)))
                pen2.setWidthF(2.8)
                pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setPen(pen2)
                p.drawLine(pt1, pt2)

                # Pass 3 – bright core
                pen3 = QPen(QColor(190, 250, 255, min(255, base_alpha + 30)))
                pen3.setWidthF(0.9)
                pen3.setCapStyle(Qt.PenCapStyle.RoundCap)
                p.setPen(pen3)
                p.drawLine(pt1, pt2)

        # ── 4. Rim glow halo ──
        p.setClipping(False)
        rim = QRadialGradient(QPointF(cx, cy), r + 14)
        rim.setColorAt(0.72, QColor(0, 210, 235, 0))
        rim.setColorAt(0.86, QColor(0, 220, 245, 55))
        rim.setColorAt(1.00, QColor(0, 200, 225, 0))
        p.setBrush(QBrush(rim))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), r + 14, r + 14)

        p.end()


# ──────────────────────────────────────────────
#  Main Overlay
# ──────────────────────────────────────────────
class VeroraOverlay(QWidget):

    def __init__(self):
        super().__init__()
        self._listening = True
        self._user_name = "Kairo"
        self._transcript = ""
        self._drag_pos = None
        self.init_ui()
    
    # --- NEW: Poll the state store every 500ms ---
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_state)
        self._poll_timer.start(500)

    def _poll_state(self):
        s = store.get_all()
        cpu = s.get("system_cpu", 0)
        ram = s.get("system_ram", 0)
        gpu = s.get("system_gpu_util", "N/A")
        loss = s.get("metric_loss", None)
        acc = s.get("metric_accuracy", None)
        file = s.get("last_modified_file", "None")
        
        # Start formatting the live telemetry (always show system stats)
        telemetry = (
            f"<b>CPU:</b> {cpu}% | <b>RAM:</b> {ram}%<br>"
            f"<b>GPU:</b> {gpu}<br>"
        )
        
        # Only add the ML metrics line if they actually exist
        if loss is not None and acc is not None:
            telemetry += f"<b>Loss:</b> {loss} | <b>Acc:</b> {acc}<br>"
            
        # Always show the last modified file at the bottom
        telemetry += f"<b>Last File:</b> {file}"
        
        # Update the UI
        self.transcript_label.setText(f'<div style="text-align:center;">{telemetry}</div>')

    # ── background paint ─────────────────────

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        radius = 24.0

        # Dark purple card
        bg = QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0.0, QColor(22, 14, 52))
        bg.setColorAt(1.0, QColor(14, 8, 38))

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.setBrush(QBrush(bg))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)

        # Subtle border
        border_pen = QPen(QColor(120, 80, 200, 60))
        border_pen.setWidthF(1.5)
        p.setPen(border_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()

    # ── drag to move ──────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    # ── UI init ──────────────────────────────

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(260, 380)

        # Centre on screen (bottom-right feel)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 300, screen.height() - 440)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 22, 20, 24)
        outer.setSpacing(0)

        # ── Top: "Hi, I'm listening…" ──
        self.status_label = QLabel("Hi, I'm listening...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: rgba(200, 190, 240, 200);
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 400;
            letter-spacing: 0.5px;
        """)
        outer.addWidget(self.status_label)

        outer.addSpacing(14)

        # ── Orb ──
        orb_row = QHBoxLayout()
        orb_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orb = HoloOrb()
        orb_row.addWidget(self.orb)
        outer.addLayout(orb_row)

        outer.addSpacing(18)

        # ── Bottom: transcript / conversation ──
        self.transcript_label = QLabel("")
        self.transcript_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet("""
            color: rgba(220, 215, 245, 220);
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 400;
            line-height: 1.5;
        """)
        outer.addWidget(self.transcript_label)

        outer.addStretch()

    # ── Public API ───────────────────────────

    def set_listening(self, is_listening: bool):
        self._listening = is_listening
        if is_listening:
            self.status_label.setText("Hi, I'm listening...")
        else:
            self.status_label.setText("Processing...")

    def update_transcript(self, user_name: str, text: str):
        """Display transcript with the user name highlighted."""
        self._user_name = user_name
        self._transcript = text
        # Build rich text with highlighted name
        highlighted = (
            f'<span style="color: #F5A623; font-weight: 600;">{user_name}</span>'
        )
        self.transcript_label.setText(
            f'<div style="text-align:center;">Hey {highlighted}, '
            f'{text}</div>'
        )

    def update_status(self, file=None, accuracy=None, status=None):
        """Legacy compatibility shim."""
        if status:
            self.status_label.setText(f"Status: {status}")


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
def run_overlay():
    app = QApplication(sys.argv)

    overlay = VeroraOverlay()
    overlay.show()

    # Demo: show a transcript after 1.5 s
    def demo_transcript():
        overlay.update_transcript(
            "Verora",
            "give me some examples of popular design trends for the end of 2024..."
        )

    QTimer.singleShot(3000, demo_transcript)

    sys.exit(app.exec())


if __name__ == "__main__":
    run_overlay()