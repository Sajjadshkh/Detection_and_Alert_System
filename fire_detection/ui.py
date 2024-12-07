from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import sys
import cv2
import time
from fire_detection.detector import detect_fire
from queue import Queue

ALERT_INTERVAL = 90
alert_queue = Queue()


video_sources = [
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/fire3.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/fire1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random3.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random2.mp4"
    ]

# دیکشنری برای نام اتاق‌ها
rooms = {
    "101": "Living Room",
    "102": "Kitchen",
    "103": "Bedroom",
    "104": "Bathroom",
    "105": "Office", 
    "106": "Rest"
}

class VideoWindow(QMainWindow):
    def __init__(self, video_source, window_name, room_id):
        super().__init__()
        self.setWindowTitle(window_name)
        self.video_source = video_source
        self.room_id = room_id
        self.last_alert_time = 0

        self.room_label = QLabel(rooms.get(self.room_id, "Unknown Room"), self)
        self.room_label.setAlignment(Qt.AlignCenter)
        self.room_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.label = QLabel(self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.room_label) 
        self.layout.addWidget(self.label)

        self.widget = QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) 

        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {video_source}")
            return

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.close()
            return

        frame, fire_detected = detect_fire(frame)

        if fire_detected and time.time() - self.last_alert_time > ALERT_INTERVAL:
            self.last_alert_time = time.time()
            room_name = rooms.get(self.room_id, "Unknown Room") 
            alert_message = f"Fire detected in {room_name} (Room {self.room_id})"
            alert_queue.put(alert_message) 

        h, w, c = frame.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

def start_ui():
    app = QApplication(sys.argv)

    main_window = QMainWindow()

    grid_layout = QGridLayout()


    windows = []
    for idx, video_source in enumerate(video_sources):
        room_id = str(101 + idx)
        room_name = rooms.get(room_id, "Unknown Room") 
        window = VideoWindow(video_source, f"Video {idx + 1} - {room_name}", room_id)
        row = idx // 3
        col = idx % 3 
        grid_layout.addWidget(window, row, col) 
        window.show() 
        windows.append(window)

    grid_layout.setHorizontalSpacing(0) 
    grid_layout.setVerticalSpacing(0) 

    for window in windows:
        window.label.setFixedSize(460, 300)

    central_widget = QWidget()
    central_widget.setLayout(grid_layout)
    main_window.setCentralWidget(central_widget)

 
    main_window.show()

    sys.exit(app.exec_())