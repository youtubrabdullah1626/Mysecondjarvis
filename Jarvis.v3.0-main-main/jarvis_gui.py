# nova_fixed.py
# J.A.R.V.I.S HUD — Fixed GUI
# Requires: PySide6, psutil, opencv-python, deepface
# Run: pip install PySide6 psutil opencv-python deepface

import sys, math, random, time, os
from datetime import datetime
try:
    import psutil
except:
    psutil = None

cv2 = None
DeepFace = None

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QRadialGradient, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QGridLayout

# ---------- Helpers ----------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def smoothstep(edge0, edge1, x):
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)

# ---------- Widgets ----------
class SectionTitle(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("color:#CFE7FF; font-weight:600; font-size:10px; letter-spacing:0.5px;")

class CameraWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame { 
                background: rgba(12,16,22,230); 
                border-radius:8px; 
                border:1px solid rgba(120,160,220,30);
                max-width: 320px;
                max-height: 240px;
            }
            QLabel { 
                color:#DCECFB; 
                font-size:10px; 
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.title = SectionTitle("LIVE CAMERA")
        self.video_label = QLabel("Initializing...")
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addWidget(self.video_label, 1)

        global cv2
        try:
            if cv2 is None:
                import cv2 as _cv2
                cv2 = _cv2
        except Exception as e:
            print(f"[CameraWidget] cv2 import failed: {e}")
            cv2 = None

        try:
            self.capture = cv2.VideoCapture(0) if cv2 else None
            if cv2:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            else:
                self.face_cascade = None
        except:
            self.face_cascade = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        if cv2 is None or self.capture is None:
            return
        ret, frame = self.capture.read()
        if not ret:
            return
        frame = cv2.resize(frame, (320,240))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.face_cascade:
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w,y+h), (100,220,255), 2)
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch*w, QImage.Format_BGR888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def stop_camera(self):
        self.timer.stop()
        try:
            if self.capture and self.capture.isOpened():
                self.capture.release()
        except:
            pass

class NeonBar(QWidget):
    def __init__(self, title, init=0.0, style='rainbow'):
        super().__init__()
        self.title = title
        try:
            self.value = float(init)
        except:
            self.value = 0.0
        self.unit = ""
        self.setMinimumHeight(40)  # Reduced height
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.style = style
    def setValue(self, v):
        self.value = clamp(float(v), 0.0, 100.0)
        self.update()
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(6,6,-6,-6)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(14,18,24,220))
        p.drawRoundedRect(self.rect(), 8, 8)
        p.setPen(QColor(170,190,210))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        p.drawText(r.x(), r.y()-2, r.width(), 16, Qt.AlignLeft|Qt.AlignTop, self.title.upper())
        bar = QRectF(r.x(), r.y()+16, r.width(), 10)
        p.setBrush(QColor(28,36,48,220))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar, 6,6)
        w = bar.width() * (self.value/100.0)
        fill = QRectF(bar.x(), bar.y(), w, bar.height())
        grad = QLinearGradient(fill.topLeft(), fill.topRight())
        if self.style=='rainbow':
            grad.setColorAt(0.0, QColor(30,220,140))
            grad.setColorAt(0.5, QColor(255,200,60))
            grad.setColorAt(1.0, QColor(255,90,80))
        elif self.style=='pink':
            grad.setColorAt(0.0, QColor(255,100,220))
            grad.setColorAt(1.0, QColor(200,50,255))
        elif self.style=='green':
            grad.setColorAt(0.0, QColor(40,220,120))
            grad.setColorAt(1.0, QColor(20,160,100))
        else:
            grad.setColorAt(0.0, QColor(80,200,255))
            grad.setColorAt(1.0, QColor(150,120,255))
        p.setBrush(grad)
        p.drawRoundedRect(fill,6,6)
        p.setPen(QColor(230,240,255))
        p.setFont(QFont("Consolas", 10, QFont.DemiBold))
        txt = f"{int(self.value)}{self.unit if self.unit else '%'}"
        p.drawText(r, Qt.AlignRight|Qt.AlignVCenter, txt)

class StatCard(QFrame):
    def __init__(self, title, bars):
        super().__init__()
        self.setStyleSheet("QFrame { background: rgba(12,16,22,230); border-radius:10px; border:1px solid rgba(120,160,220,30); }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8,8,8,8)
        lay.setSpacing(6)
        lay.addWidget(SectionTitle(title))
        for b in bars: lay.addWidget(b)

class NetworkStats(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { background: rgba(12,16,22,230); border-radius:10px; border:1px solid rgba(120,160,220,30); } QLabel { color:#DCECFB; font-size:11px; }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8,8,8,8)
        lay.setSpacing(4)
        self.ip = QLabel("IP: 0.0.0.0")
        self.up = QLabel("Upload: 0.0 MB/s")
        self.down = QLabel("Download: 0.0 MB/s")
        lay.addWidget(self.ip)
        lay.addWidget(self.up)
        lay.addWidget(self.down)
        lay.addStretch()
        self.ip.hide()  # Hide IP

class ClockCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { background: rgba(12,16,22,230); border-radius:10px; } QLabel { color:#EAF6FF; }")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8,8,8,8)
        self.timeLbl = QLabel("--:--:--")
        self.timeLbl.setStyleSheet("font-size:28px; font-weight:700;")
        self.dateLbl = QLabel("")
        self.dateLbl.setStyleSheet("color:#AFC7DA; font-size:11px;")
        lay.addWidget(self.timeLbl)
        lay.addWidget(self.dateLbl)
    def tick(self):
        now = datetime.now()
        self.timeLbl.setText(now.strftime("%H:%M:%S"))
        self.dateLbl.setText(now.strftime("%A, %d %b %Y"))

class AnimatedRings(QWidget):
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.click_boost = 0.0
        self.setMinimumSize(400,400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()
        radius = min(rect.width(), rect.height()) * 0.42
        bg = QRadialGradient(QPointF(cx,cy), radius*1.8)
        bg.setColorAt(0.0, QColor(10,12,16))
        bg.setColorAt(1.0, QColor(6,8,12,0))
        p.fillRect(rect, bg)
        rings = [
            (radius*1.02, 9.0, 0.00, QColor(80,220,255,220)),
            (radius*0.86, 6.0, 0.19, QColor(255,160,90,210)),
            (radius*0.72, 4.0, 0.36, QColor(180,120,255,200)),
            (radius*0.59, 3.0, 0.54, QColor(100,220,200,200)),
            (radius*0.46, 2.2, 0.72, QColor(255,110,200,180)),
        ]
        for r, w, off, col in rings:
            w += self.click_boost*2  # enlarge on click
            self._draw_ring(p, QPointF(cx,cy), r, w, off, col)
        p.setPen(QColor(200,240,255))
        p.setFont(QFont("Segoe UI", 36, QFont.Black))
        p.drawText(rect, Qt.AlignCenter, "J.A.R.V.I.S")
        self.click_boost *= 0.92  # fade effect

    def _draw_ring(self, p, center, radius, width, offset, color):
        base = (self.phase + offset) % 1.0
        for i in range(2):
            start = (base + i*0.48) * 360.0
            span = 200.0 if i==0 else 120.0
            pen = QPen(color, width)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            rect = QRectF(center.x()-radius, center.y()-radius, radius*2, radius*2)
            p.drawArc(rect, int(-start*16), int(-span*16))

    def mousePressEvent(self, event):
        self.click_boost = 4.0  # trigger click animation

class TitleBar(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("QFrame{ background: rgba(12,16,22,200); border-bottom:1px solid rgba(120,160,220,25); } QLabel{ color:#DDEFFB; font-weight:700; }")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8,4,8,4)
        lbl = QLabel(title)
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lay.addWidget(lbl)
        lay.addStretch()

class NovaHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S HUD")
        self.resize(1200,720)
        self.setStyleSheet("background-color: #071018;")

        top = TitleBar("J.A.R.V.I.S VISION INTERFACE")
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8,8,8,8)
        root.setSpacing(8)
        root.addWidget(top)

        body = QGridLayout()
        body.setSpacing(8)
        root.addLayout(body,1)

        # LEFT TOP card (CPU PROFILES)
        self.cpu_util = NeonBar("CPU UTILIZATION", init=65)
        self.cpu_temp = NeonBar("CPU TEMPERATURE", init=62)
        self.battery = NeonBar("BATTERY", init=72)
        leftCard = StatCard("SYSTEM PROFILES", [self.cpu_util, self.cpu_temp, self.battery])
        body.addWidget(leftCard,0,0,1,1)

        # LEFT BOTTOM: Camera
        self.camera_view = CameraWidget()
        body.addWidget(self.camera_view,1,0,1,1)

        # CENTER: animated rings
        self.rings = AnimatedRings()
        body.addWidget(self.rings,0,1,2,1)

        # RIGHT TOP: Storage Stats
        self.mem = NeonBar("MEMORY USAGE", init=50, style='pink')
        self.disk = NeonBar("DISK USAGE", init=75, style='green')
        rightCard = StatCard("STORAGE STATS", [self.mem, self.disk])
        body.addWidget(rightCard,0,2,1,1)

        # RIGHT BOTTOM: network + clock
        rightLower = QVBoxLayout(); rightLower.setSpacing(6)
        self.net = NetworkStats()
        self.clock = ClockCard()
        rightLower.addWidget(self.net)
        rightLower.addWidget(self.clock)
        rightWrap = QWidget(); rightWrap.setLayout(rightLower)
        body.addWidget(rightWrap,1,2,1,1)

        body.setColumnStretch(0,1); body.setColumnStretch(1,2); body.setColumnStretch(2,1)
        body.setRowStretch(0,1); body.setRowStretch(1,1)

        # timers
        self.animTimer = QTimer(self); self.animTimer.timeout.connect(self.animate); self.animTimer.start(16)
        self.statTimer = QTimer(self); self.statTimer.timeout.connect(self.sampleStats); self.statTimer.start(1000)
        self.clockTimer = QTimer(self); self.clockTimer.timeout.connect(self.tick); self.clockTimer.start(1000)
        self.last_bytes = None
        self.sampleStats()
        self.tick()

    def animate(self):
        self.rings.phase = (self.rings.phase + 0.0075) % 1.0
        self.rings.update()

    def tick(self):
        self.clock.tick()

    def sampleStats(self):
        try: cpu = psutil.cpu_percent() if psutil else random.uniform(8,88)
        except: cpu = random.uniform(8,88)
        self.cpu_util.setValue(cpu)
        temp_c = None
        if psutil:
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for k,v in temps.items():
                        if v: temp_c = v[0].current; break
            except: temp_c = None
        if temp_c is None: temp_c = 48 + 12*math.sin(time.time()/6.5) + random.uniform(-2,2)
        self.cpu_temp.setValue(clamp(temp_c,0,100))
        batt_pct = None
        if psutil and hasattr(psutil,"sensors_battery"):
            try:
                b = psutil.sensors_battery()
                if b: batt_pct = b.percent
            except: batt_pct = None
        if batt_pct is None: batt_pct = 70 + 8*math.sin(time.time()/10.0) + random.uniform(-4,4)
        self.battery.setValue(clamp(batt_pct,0,100))
        try: mem_pct = psutil.virtual_memory().percent if psutil else random.uniform(22,86)
        except: mem_pct=random.uniform(22,86)
        self.mem.setValue(mem_pct)
        try: disk_pct = psutil.disk_usage('/').percent if psutil else random.uniform(12,88)
        except: disk_pct=random.uniform(12,88)
        self.disk.setValue(disk_pct)

    def closeEvent(self,event):
        self.camera_view.stop_camera()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    w = NovaHUD(); w.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
