import sys
import cv2
import os
import time
import math
import numpy as np
from fire_detection.detector import detect_fire
from queue import Queue
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QGridLayout, QPushButton, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from functools import partial


ALERT_INTERVAL = 90
alert_queue = Queue()


video_sources = [
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/fire2.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random3.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4",
    "/Users/sajjad/Documents/GitHub/Detection_and_Alert_System/videos/random1.mp4"
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
        

    def start_recording(self):
        output_dir = os.path.join(os.getcwd(), "recordings")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"fire_{self.room_id}_{int(time.time())}.avi")

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 30
        frame_size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        self.out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
        self.recording = True

    def stop_recording(self):
        self.recording = False
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

                # start recording
                if not self.recording:
                    self.start_recording()

                if self.recording and self.out:
                    self.out.write(frame)

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

                # stop recording
                if self.recording:
                    self.stop_recording()


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
    QPushButton {
        font-family: Arial, sans-serif;
        font-size: 14px;
        font-weight: bold;
        color: white;
        background-color: #007BFF;
        border: 2px solid #0056b3;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 5px 0;
        text-align: center;
    }
    QPushButton:hover {
        background-color: #0056b3;
    }
    QPushButton:pressed {
        background-color: #003f7f;
    }
""")


    main_window = QMainWindow()
    main_window.setWindowTitle("Fire Detection and Alert System")
    main_window.setMinimumSize(1100, 700)


    grid_layout = QGridLayout()


    def update_layout(rows, cols):
        """Update the grid layout dynamically based on the selected rows and columns."""
        for i in reversed(range(grid_layout.count())):
            widget = grid_layout.itemAt(i).widget()
            grid_layout.removeWidget(widget)
            widget.setParent(None)
        for idx, video_source in enumerate(video_sources):
            room_id = str(101 + idx)  # Map video sources to room IDs
            video_window = VideoWindow(video_source, f"Video {idx + 1}", room_id)
            row = idx // cols
            col = idx % cols
            grid_layout.addWidget(video_window, row, col)
        grid_layout.setSpacing(5)


    def calculate_grid_options():
        """Calculate optimal grid layout options based on the number of video sources."""
        n = len(video_sources)
        options = []
        seen = set()

        for rows in range(2, n + 1):
            cols = math.ceil(n / rows)
            
            if rows != 1 and cols != 1 and rows * cols >= n:
                if (rows, cols) not in seen and (cols, rows) not in seen:
                    if rows <= cols:
                        options.append((rows, cols))
                        seen.add((rows, cols))
                    if cols <= rows and (cols, rows) not in seen:
                        options.append((cols, rows))
                        seen.add((cols, rows))
        return options


    # Create a layout for the main UI
    main_layout = QVBoxLayout()


    # Add a button with a dropdown menu
    layout_button = QPushButton("Change Layout")
    layout_button.setIcon(QIcon.fromTheme("view-grid"))  # Add an icon (if available)
    layout_menu = QMenu()


    grid_options = calculate_grid_options()
    for rows, cols in grid_options:
        action = QAction(f"{rows}x{cols} Layout", layout_menu)
        action.triggered.connect(partial(update_layout, rows, cols))  # Update layout with rows and columns
        layout_menu.addAction(action)


    layout_button.setMenu(layout_menu)


    # Add grid layout and button to main layout
    main_layout.addWidget(layout_button)
    main_layout.addLayout(grid_layout)


    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    main_window.setCentralWidget(central_widget)


    # Initialize the default layout
    def calculate_default_layout():
        width = main_window.width()
        height = main_window.height()
        if width > height:
            return 2, 3
        return 3, 2 

    default_rows, default_cols = calculate_default_layout()
    update_layout(default_rows, default_cols)

    main_window.show()
    sys.exit(app.exec_())