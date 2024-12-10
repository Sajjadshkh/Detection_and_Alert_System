import os
import time
import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from fire_detection.detector import detect_fire
from ui.config import rooms

class VideoWindow(QMainWindow):
    def __init__(self, video_source, window_name, room_id):
        super().__init__()

        self.setWindowTitle(window_name)
        self.video_source = video_source
        self.room_id = room_id
        self.last_alert_time = 0
        self.recording = False
        self.out = None

        # Room label
        self.room_label = QLabel(rooms.get(self.room_id, "Unknown Room"), self)
        self.room_label.setAlignment(Qt.AlignCenter)

        # Fire status label
        self.fire_status_label = QLabel("Status: Normal", self)
        self.fire_status_label.setAlignment(Qt.AlignCenter)

        # Video label for displaying video feed
        self.label = QLabel(self)
        self.label.setStyleSheet("border: 1px solid #000000;")
        self.label.setAlignment(Qt.AlignCenter)

        # Layouts
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.room_label)
        self.layout.addWidget(self.fire_status_label)
        self.layout.addWidget(self.label)

        self.widget = QWidget(self)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Timer to periodically update the video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

        # Initialize video capture
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            print(f"Error: Could not open video source {video_source}")
            return

        # Predefined styles for the labels to avoid repetitive styling
        self.normal_status_style = """
            color: #4CAF50;
            font-size: 14px;
            font-weight: bold;
            background-color: #E0E0E0;
            border-radius: 8px;
            padding: 5px;
        """
        self.fire_status_style = """
            color: white;
            font-size: 14px;
            font-weight: bold;
            background-color: #FF5722;
            border-radius: 8px;
            padding: 5px;
        """
        self.no_signal_status_style = """
            color: #000000;
            font-size: 14px;
            font-weight: bold;
            background-color: #FFCC00;
            border-radius: 8px;
            padding: 5px;
        """

    def start_recording(self):
        """Start recording the video when fire is detected."""
        if self.recording:
            return

        # Create recording directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"fire_{self.room_id}_{int(time.time())}.avi")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30  # Default to 30 fps if not available
        frame_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        # Initialize video writer
        self.out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        self.recording = True

    def stop_recording(self):
        """Stop video recording when fire is no longer detected."""
        if self.recording:
            self.recording = False
            if self.out:
                self.out.release()
                self.out = None

    def update_frame(self):
        """Capture video frame and process for fire detection."""
        ret, frame = self.cap.read()

        # If video ends, reset to the first frame and continue
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
            ret, frame = self.cap.read()
            if not ret:
                frame = np.zeros((360, 640, 3), dtype=np.uint8)
                self.fire_status_label.setText("Status: No Signal")
                self.fire_status_label.setStyleSheet(self.no_signal_status_style)
        else:
            # Fire detection
            frame, fire_detected = detect_fire(frame)

            # Update fire status and manage recording
            if fire_detected:
                self.fire_status_label.setText("Status: Fire Detected")
                self.fire_status_label.setStyleSheet(self.fire_status_style)

                if not self.recording:
                    self.start_recording()

                if self.recording and self.out:
                    self.out.write(frame)
            else:
                self.fire_status_label.setText("Status: Normal")
                self.fire_status_label.setStyleSheet(self.normal_status_style)

                if self.recording:
                    self.stop_recording()

        # Resize frame to fit the label
        label_width = self.label.width()
        label_height = self.label.height()

        # Resize the frame to fit the label size
        frame_resized = cv2.resize(frame, (label_width, label_height), interpolation=cv2.INTER_LINEAR)

        # Convert frame to QImage and then to QPixmap
        h, w, c = frame_resized.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)

        # Scale the pixmap to fit the label size
        self.label.setPixmap(pixmap.scaled(label_width, label_height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        font_size = max(self.width() // 40, 10)
        self.room_label.setStyleSheet(f"""
            font-size: {font_size}px;
            font-weight: bold;
            color: #ffffff;
            background-color: #4CAF50;
            border-radius: 8px;
            padding: {font_size // 2}px;
        """)

        if self.label.pixmap():
            self.label.setPixmap(
                self.label.pixmap().scaled(
                    self.label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

    def closeEvent(self, event):
        """Release resources on close."""
        if self.cap.isOpened():
            self.cap.release()
        if self.out:
            self.out.release()
        super().closeEvent(event)