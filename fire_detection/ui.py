import sys
import cv2
import numpy as np
from fire_detection.detector import detect_fire
from queue import Queue
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QTextEdit

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

# room names
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

        # name rooms label
        self.room_label = QLabel(rooms.get(self.room_id, "Unknown Room"), self)
        self.room_label.setAlignment(Qt.AlignCenter)
        self.room_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background-color: #4CAF50;
            border-radius: 8px;
            padding: 10px;
        """)

        # fire satatus label
        self.fire_status_label = QLabel("Status: Normal", self)
        self.fire_status_label.setAlignment(Qt.AlignCenter)
        self.fire_status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #ffffff;
            background-color: #2196F3;
            border-radius: 8px;
            padding: 5px;
        """)


       # video label
        self.label = QLabel(self)
        self.label.setStyleSheet("border: 1px solid #000000;")

        # layouts
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.room_label)
        self.layout.addWidget(self.fire_status_label)
        self.layout.addWidget(self.label)

        self.widget = QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {video_source}")
            return

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:    # if video ended
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)    # play video again
            ret, frame = self.cap.read() 
            if not ret:
                frame = np.zeros((360, 640, 3), dtype=np.uint8)
                self.fire_status_label.setText("Status: No Signal")
                self.fire_status_label.setStyleSheet("""
                    color: #000000;
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #FFCC00;
                    border-radius: 8px;
                    padding: 5px;
                """)
        else:
            # detect fire
            frame, fire_detected = detect_fire(frame)

            # update status and save alert history label
            if fire_detected:
                self.fire_status_label.setText("Status: Fire Detected")
                self.fire_status_label.setStyleSheet("""
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #FF5722;
                    border-radius: 8px;
                    padding: 5px;
                """)
            else:
                self.fire_status_label.setText("Status: Normal")
                self.fire_status_label.setStyleSheet("""
                    color: #4CAF50;
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #E0E0E0;
                    border-radius: 8px;
                    padding: 5px;
                """)


        h, w, c = frame.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        self.timer.stop()
        event.accept()

def start_ui():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            font-family: Arial, sans-serif;
        }
        QTextEdit {
            font-family: 'Courier New', Courier, monospace;
        }
    """)

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
        window.label.setFixedSize(500, 360)

    central_widget = QWidget()
    central_widget.setLayout(grid_layout)
    main_window.setCentralWidget(central_widget)

 
    main_window.show()

    sys.exit(app.exec_())