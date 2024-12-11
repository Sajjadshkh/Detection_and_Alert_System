import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QScrollArea
from ui.video_window import VideoWindow
from ui.config import video_sources


def start_ui():
    app = QApplication(sys.argv)

    def load_stylesheet():
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles", "styles.css")
        if not os.path.exists(file_path):
            print(f"Error: Stylesheet file not found at {file_path}")
            return ""
        with open(file_path, "r") as file:
            return file.read()

    app.setStyleSheet(load_stylesheet())

    if not video_sources:
        print("Error: No video sources provided.")
        sys.exit(1)

    main_window = QMainWindow()
    main_window.setWindowTitle("Fire Detection and Alert System")
    main_window.setMinimumSize(1100, 700)

    grid_layout = QGridLayout()

    rows, cols = 3, 3

    # Add video windows to the grid layout based on video_sources
    for idx, video_source in enumerate(video_sources):
        room_id = str(101 + idx)  # Map video sources to room IDs
        video_window = VideoWindow(video_source, f"Video {idx + 1}", room_id)
        row = idx // rows  # Define number of rows (fixed at 3 for now)
        col = idx % cols  # Define number of columns (fixed at 3 for now)
        grid_layout.addWidget(video_window, row, col)

    grid_layout.setSpacing(5)

    # Create a layout for the main UI
    main_layout = QVBoxLayout()

    # Add grid layout to the main layout
    main_layout.addLayout(grid_layout)

    scroll_area = QScrollArea()
    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(central_widget)

    main_window.setCentralWidget(scroll_area)

    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    main_window.setCentralWidget(central_widget)
    main_window.setGeometry(100, 100, 1100, 700)

    main_window.show()
    sys.exit(app.exec_())