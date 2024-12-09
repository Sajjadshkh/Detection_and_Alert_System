import sys
import cv2
import os
import numpy as np
from fire_detection.detector import detect_fire
from queue import Queue
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QPushButton
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
        self.recording = False
        self.out = None


        # save video button
        self.save_button = QPushButton("Save Video", self)
        self.save_button.clicked.connect(self.toggle_recording)
        self.save_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                background-color: #6A1B9A;
                border: 2px solid #AB47BC;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #8E24AA;
            }
            QPushButton:pressed {
                background-color: #4A148C;
                border: 2px solid #CE93D8;
            }
        """)

    
        # name rooms label
        self.room_label = QLabel(rooms.get(self.room_id, "Unknown Room"), self)
        self.room_label.setAlignment(Qt.AlignCenter)

        # fire status label
        self.fire_status_label = QLabel("Status: Normal", self)
        self.fire_status_label.setAlignment(Qt.AlignCenter)

        # video label
        self.label = QLabel(self)
        self.label.setStyleSheet("border: 1px solid #000000;")
        self.label.setAlignment(Qt.AlignCenter)

        # layouts
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.room_label)
        self.layout.addWidget(self.fire_status_label)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.save_button)

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
        

    def toggle_recording(self):
        if not self.recording:
            # Start recording
            output_dir = os.path.join(os.getcwd(), "recordings")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"recorded_{self.room_id}.avi")

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
            frame_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

            self.out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
            self.recording = True
            self.save_button.setText("Stop Recording")
        else:
            # Stop recording
            self.recording = False
            self.save_button.setText("Save Video")
            if self.out:
                self.out.release()
                self.out = None

                


    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:  # if video ended
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # play video again
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
            if self.recording and self.out:
                self.out.write(frame)


        # get the current size of the label
        label_width = self.label.width()
        label_height = self.label.height()

        # Get the frame size and scale the video to a larger size
        frame_resized = cv2.resize(frame, (label_width, label_height), interpolation=cv2.INTER_LINEAR)

        h, w, c = frame_resized.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)

        # scale the pixmap to fit the label size while keeping the aspect ratio
        self.label.setPixmap(pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        if self.label.pixmap():
            # scale the pixmap to fit the label size while keeping the aspect ratio
            self.label.setPixmap(
                self.label.pixmap().scaled(
                    self.label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        
        # dynamically adjust font size for labels based on window size
        font_size = max(self.width() // 40, 10)  # Set a reasonable minimum font size
        self.room_label.setStyleSheet(f"font-size: {font_size}px; font-weight: bold; color: #ffffff; background-color: #4CAF50; border-radius: 8px; padding: 10px;")
        self.fire_status_label.setStyleSheet(f"font-size: {font_size * 0.8}px; font-weight: bold; color: #ffffff; background-color: #2196F3; border-radius: 8px; padding: 5px;")
        
        super().resizeEvent(event)

    def closeEvent(self, event):
        if self.cap.isOpened():
            self.cap.release()
        if self.out:
            self.out.release()
        super().closeEvent(event)


def start_ui():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
    QMainWindow {
        background-color: #f9f9f9;
    }
    QLabel {
        font-family: Arial, sans-serif;
        font-size: 14px;
        padding: 5px;
        color: #333;
    }
    QTextEdit {
        font-family: 'Courier New', Courier, monospace;
        font-size: 12px;
        background-color: #fff;
        border: 1px solid #ccc;
    }
    QVBoxLayout {
        margin: 10px;
    }
""")

    main_window = QMainWindow()

    main_window.setWindowTitle("Fire Detection and Alert System")

    main_window.setMinimumSize(1100, 700)

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

    grid_layout.setHorizontalSpacing(15)
    grid_layout.setVerticalSpacing(15)

    grid_layout.setContentsMargins(10, 10, 10, 10)
    grid_layout.setSpacing(10)

    central_widget = QWidget()
    central_widget.setLayout(grid_layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()

    sys.exit(app.exec_())