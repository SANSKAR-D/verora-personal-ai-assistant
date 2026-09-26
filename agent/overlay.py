import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMessageBox, QPushButton, QDialog
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QRadialGradient, QLinearGradient,
    QPainterPath, QFont, QPen, QBrush
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from state_store.state import store

class OverlaySignals(QObject):
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()
    update_signal = pyqtSignal(str)
    large_text_signal = pyqtSignal(str)
    prompt_signal = pyqtSignal(str)
signals = OverlaySignals()

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
#  Permission Dialog
# ──────────────────────────────────────────────
class PermissionDialog(QDialog):
    def __init__(self, description: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 220)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title = QLabel("Permission Required")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: rgba(220, 215, 245, 255);
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        desc = QLabel(description)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("""
            color: rgba(200, 190, 240, 200);
            font-size: 13px;
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.4;
        """)
        layout.addWidget(desc)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        
        btn_no = QPushButton("✕ Deny")
        btn_yes = QPushButton("✓ Allow")
        
        btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_style = """
            QPushButton {
                background-color: rgba(120, 80, 200, 30);
                color: rgba(200, 190, 240, 220);
                border: 1px solid rgba(120, 80, 200, 60);
                padding: 8px 0;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(140, 100, 220, 60);
                border: 1px solid rgba(140, 100, 220, 100);
            }
            QPushButton:pressed {
                background-color: rgba(100, 60, 180, 80);
            }
        """
        
        yes_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 180, 216, 80), stop:1 rgba(0, 119, 182, 80));
                color: white;
                border: 1px solid rgba(0, 180, 216, 120);
                padding: 8px 0;
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 180, 216, 120), stop:1 rgba(0, 119, 182, 120));
                border: 1px solid rgba(0, 180, 216, 160);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 180, 216, 50), stop:1 rgba(0, 119, 182, 50));
            }
        """
        
        btn_no.setStyleSheet(btn_style)
        btn_yes.setStyleSheet(yes_style)
        
        btn_no.clicked.connect(self.reject)
        btn_yes.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_no)
        btn_layout.addWidget(btn_yes)
        layout.addLayout(btn_layout)

    def paintEvent(self, _event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(0, 0, self.width(), self.height())
        radius = 16.0

        bg = QLinearGradient(0, 0, 0, self.height())
        bg.setColorAt(0.0, QColor(22, 14, 52, 250))
        bg.setColorAt(1.0, QColor(14, 8, 38, 250))

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        p.setBrush(QBrush(bg))
        
        border_pen = QPen(QColor(120, 80, 200, 80))
        border_pen.setWidthF(1.5)
        p.setPen(border_pen)
        
        p.drawPath(path)

# ──────────────────────────────────────────────
#  Main Overlay
# ──────────────────────────────────────────────
class VeroraOverlay(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()
    
    # --- NEW: Poll the state store every 500ms ---
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_state)
        self._poll_timer.start(500)

        self.hide()

    def show_overlay(self):
        self.show()
        self.raise_()
        
    def hide_overlay(self):
        self.hide()

    def _poll_state(self):
        s = store.get_all()
        cpu = s.get("system_cpu", 0)
        ram = s.get("system_ram", 0)
        gpu = s.get("system_gpu_util", "N/A")
        loss = s.get("metric_loss", None)
        acc = s.get("metric_accuracy", None)
        file = s.get("last_modified_file", "None")
        
        telemetry = f"CPU: {cpu}% | RAM: {ram}% | GPU: {gpu}<br>"
        if loss is not None and acc is not None:
            telemetry += f"Loss: {loss} | Acc: {acc}<br>"
        telemetry += f"Last File: {file}"
        
        # Send telemetry to the tiny bottom label instead of the transcript label
        self.telemetry_label.setText(f'<div style="text-align:center;">{telemetry}</div>')

    def handle_voice_update(self, text: str):
        if text in ["Listening...", "Speaking..."]:
            self.status_label.setText(text)
            if text == "Listening...":
                self.transcript_label.setText("")
        elif text == "":
            self.status_label.setText("Waiting...")
            self.transcript_label.setText("")
        else:
            self.transcript_label.setText(f'<div style="text-align:center;">{text}</div>')

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

    def show_large_text(self, text: str):
        try:
            print(f"[Overlay] show_large_text called with {len(text)} chars")
            if not hasattr(self, '_large_overlay'):
                self._large_overlay = LargeTextOverlay()
            self._large_overlay.show_text(text)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[Overlay] ERROR in show_large_text: {e}")



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

        # ── Middle: transcript / conversation ──
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

        outer.addSpacing(10)
        self.restart_btn = QPushButton("■")
        self.restart_btn.setFixedSize(44, 44)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.6, fx:0.5, fy:0.5, stop:0 rgba(45, 70, 80, 255), stop:1 rgba(22, 40, 45, 255));
                color: rgba(225, 95, 95, 255);
                border: 1px solid rgba(15, 30, 35, 200);
                border-radius: 22px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.6, fx:0.5, fy:0.5, stop:0 rgba(55, 85, 95, 255), stop:1 rgba(26, 48, 55, 255));
                color: rgba(255, 110, 110, 255);
            }
            QPushButton:pressed {
                background-color: rgba(18, 32, 38, 255);
            }
        """)
        self.restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_btn.clicked.connect(self._on_restart_clicked)
        outer.addWidget(self.restart_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addStretch()

        # ── Bottom: Telemetry ──
        self.telemetry_label = QLabel("")
        self.telemetry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.telemetry_label.setStyleSheet("""
            color: rgba(150, 150, 180, 150);
            font-size: 10px;
            font-family: 'Segoe UI', sans-serif;
        """)
        outer.addWidget(self.telemetry_label)

    def _on_restart_clicked(self):
        store.update("cancel_task", True)
        self.status_label.setText("Restarting...")

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


    def show_prompt(self, description: str):
        dialog = PermissionDialog(description, self)
        
        screen = QApplication.primaryScreen().geometry()
        dialog.move(screen.center().x() - dialog.width() // 2, screen.center().y() - dialog.height() // 2)
        
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            store.update("confirmation_result", True)
        else:
            store.update("confirmation_result", False)


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

from PyQt6.QtWidgets import QTextBrowser, QPushButton

class LargeTextOverlay(QWidget):
    """A translucent black screen for displaying large AI responses with streaming Markdown."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.resize(int(screen.width() * 0.5), int(screen.height() * 0.7))
        self.move(int(screen.width() * 0.25), int(screen.height() * 0.15))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Add a close button at the top right
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.close_btn = QPushButton("Close (X)")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(200, 50, 50, 150);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(200, 50, 50, 255);
            }
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self._close_overlay)
        top_layout.addWidget(self.close_btn)
        layout.addLayout(top_layout)
        
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                color: rgba(230, 230, 250, 240);
                font-size: 16px;
                font-family: 'Segoe UI', sans-serif;
                border: none;
            }
        """)
        layout.addWidget(self.text_browser)
        
        # Streaming setup
        self._full_text = ""
        self._current_char_idx = 0
        self._stream_timer = QTimer(self)
        self._stream_timer.timeout.connect(self._stream_tick)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), 16, 16)
        p.setBrush(QBrush(QColor(10, 12, 20, 230))) # Translucent black
        p.setPen(QPen(QColor(120, 80, 200, 80), 1.5))
        p.drawPath(path)

    def show_text(self, text: str):
        print(f"[LargeTextOverlay] show_text called, showing window...")
        self._full_text = text
        self._current_char_idx = 0
        self.text_browser.setHtml("")
        self.show()
        self.raise_()
        self.activateWindow()
        # Start streaming 15 chars per tick (~60fps)
        self._stream_timer.start(16)
        print(f"[LargeTextOverlay] Window visible: {self.isVisible()}")

    def _stream_tick(self):
        import markdown
        if self._current_char_idx >= len(self._full_text):
            self._stream_timer.stop()
            html = markdown.markdown(self._full_text, extensions=['extra'])
            self.text_browser.setHtml(html)
            return
            
        self._current_char_idx += 15  # Speed of streaming
        if self._current_char_idx > len(self._full_text):
            self._current_char_idx = len(self._full_text)
            
        partial_text = self._full_text[:self._current_char_idx]
        html = markdown.markdown(partial_text, extensions=['extra'])
        self.text_browser.setHtml(html)
        # Scroll to bottom while streaming
        scroll = self.text_browser.verticalScrollBar()
        scroll.setValue(scroll.maximum())

    def _close_overlay(self):
        self.hide()
        self._stream_timer.stop()

    def mousePressEvent(self, event):
        self._close_overlay()
        event.accept()