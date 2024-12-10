import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QGridLayout, QPushButton
from ui.video_window import VideoWindow
from ui.config import video_sources


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

    # Add video windows to the grid layout based on video_sources
    for idx, video_source in enumerate(video_sources):
        room_id = str(101 + idx)  # Map video sources to room IDs
        video_window = VideoWindow(video_source, f"Video {idx + 1}", room_id)
        row = idx // 3  # Define number of rows (fixed at 3 for now)
        col = idx % 3  # Define number of columns (fixed at 3 for now)
        grid_layout.addWidget(video_window, row, col)

    grid_layout.setSpacing(5)

    # Create a layout for the main UI
    main_layout = QVBoxLayout()

    # Add grid layout to the main layout
    main_layout.addLayout(grid_layout)

    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    main_window.setCentralWidget(central_widget)

    main_window.show()
    sys.exit(app.exec_())