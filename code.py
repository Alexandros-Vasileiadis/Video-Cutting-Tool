import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QLabel, QSlider, QLineEdit, QFrame
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from moviepy.editor import VideoFileClip

class VideoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Editor Pro")
        self.setWindowIcon(self.style().standardIcon(getattr(self.style(), 'SP_MediaPlay')))

        # Optionally set a default font that supports emojis better:
        #     Windows example: "Segoe UI Emoji"
        #     Linux example: "Noto Color Emoji"
        # app.setFont(QFont("Segoe UI Emoji", 10))

        # Modern color palette
        self.dark_palette = QPalette()
        self.dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.WindowText, Qt.white)
        self.dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        self.dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.dark_palette.setColor(QPalette.ButtonText, Qt.white)
        self.dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197))
        self.dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(self.dark_palette)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Left panel
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setMinimumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)

        self.video_list = QListWidget()
        # Dark background for the list
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #2B2B2B;   /* pick a dark color */
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #6e40c9;
            }
        """)
        self.video_list.itemClicked.connect(self.load_video)
        left_layout.addWidget(QLabel("Available Videos:"))
        left_layout.addWidget(self.video_list)

        # Right panel
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)

        # Video display
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background: #000;")
        right_layout.addWidget(self.video_widget, 5)

        # Media player setup
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        # Custom slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #353535;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #6e40c9;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #fff;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        # Connect slider movement to set the media player position
        self.slider.sliderMoved.connect(self.set_position)

        right_layout.addWidget(self.slider)

        # Control buttons
        btn_style = """
            QPushButton {
                border: 1px solid #444;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: 500;
                color: white;
            }
            QPushButton:hover { background: #666; }
            QPushButton:pressed { background: #555; }
        """

        controls = QHBoxLayout()
        self.play_button = QPushButton("▶ Play")
        self.play_button.setStyleSheet(btn_style + "background: #4CAF50;")
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.setStyleSheet(btn_style + "background: #f44336;")
        self.pause_button.clicked.connect(self.pause_video)

        controls.addWidget(self.play_button)
        controls.addWidget(self.pause_button)
        right_layout.addLayout(controls)

        # Info display
        self.info_label = QLabel("Time: 00:00:00 | Frame: 0")
        self.info_label.setFont(QFont("Consolas", 10))
        self.info_label.setStyleSheet("color: #aaa;")
        right_layout.addWidget(self.info_label)

        # Frame navigation
        frame_nav = QHBoxLayout()
        self.frame_input = QLineEdit()
        self.frame_input.setPlaceholderText("Enter frame number")
        self.frame_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #444;
                border-radius: 4px;
                background: #353535;
                color: white;
            }
        """)
        self.go_frame_button = QPushButton("Go to Frame")
        # Ensure the text is white:
        self.go_frame_button.setStyleSheet(btn_style + "background: #777;")
        self.go_frame_button.clicked.connect(self.go_to_frame)
        frame_nav.addWidget(self.frame_input, 70)
        frame_nav.addWidget(self.go_frame_button, 30)
        right_layout.addLayout(frame_nav)

        # Cutting controls
        cut_controls = QHBoxLayout()
        self.mark_cut_button = QPushButton("✂ Mark Cut")
        self.mark_cut_button.setStyleSheet(btn_style + "background: #2196F3;")
        self.mark_cut_button.clicked.connect(self.mark_cut)

        self.perform_cuts_button = QPushButton("⏩ Export Segments")
        self.perform_cuts_button.setStyleSheet(btn_style + "background: #9C27B0;")
        self.perform_cuts_button.clicked.connect(self.perform_cuts)

        cut_controls.addWidget(self.mark_cut_button)
        cut_controls.addWidget(self.perform_cuts_button)
        right_layout.addLayout(cut_controls)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)

        # Initialize variables
        self.cut_points = []
        self.current_video_path = None
        self.video_fps = 30

        # Setup timer
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_info)
        self.timer.start()

        self.load_video_list()
        self.resize(1280, 720)

    def load_video_list(self):
        """List video files in the same directory as the script."""
        video_exts = [".mp4", ".avi", ".mov", ".mkv"]
        files = os.listdir(".")
        for f in files:
            if os.path.isfile(f) and os.path.splitext(f)[1].lower() in video_exts:
                self.video_list.addItem(f)

    def load_video(self, item):
        """Load the selected video into the media player."""
        video_file = item.text()
        self.current_video_path = os.path.abspath(video_file)
        url = QUrl.fromLocalFile(self.current_video_path)
        self.media_player.setMedia(QMediaContent(url))
        self.media_player.play()  # auto-start playback

        # Get FPS using OpenCV
        cap = cv2.VideoCapture(self.current_video_path)
        if cap.isOpened():
            self.video_fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        self.cut_points = []  # clear any previous cut points

    def play_video(self):
        self.media_player.play()

    def pause_video(self):
        self.media_player.pause()

    def set_position(self, position):
        """Set the media player's position in milliseconds (called by slider)."""
        self.media_player.setPosition(position)

    def position_changed(self, position):
        """Update the slider value when the media player position changes."""
        self.slider.setValue(position)

    def duration_changed(self, duration):
        """Set the slider's range when the media duration changes."""
        self.slider.setRange(0, duration)

    def update_info(self):
        """Update the label to show current time and computed frame."""
        position_ms = self.media_player.position()
        seconds = position_ms / 1000.0
        time_str = self.format_time(seconds)
        frame = int(seconds * self.video_fps)
        self.info_label.setText(f"Time: {time_str} | Frame: {frame}")

    def format_time(self, seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"

    def go_to_frame(self):
        """Jump to a specific frame based on FPS."""
        try:
            frame_num = int(self.frame_input.text())
        except ValueError:
            return
        seconds = frame_num / self.video_fps
        self.media_player.setPosition(int(seconds * 1000))

    def mark_cut(self):
        """Record the current playback time and computed frame as a cut point."""
        position_ms = self.media_player.position()
        seconds = position_ms / 1000.0
        frame = int(seconds * self.video_fps)
        self.cut_points.append((seconds, frame))
        # Remove duplicates and sort by time
        self.cut_points = sorted(list(set(self.cut_points)))
        print("Marked cuts:", self.cut_points)

    def perform_cuts(self):
        """Use MoviePy to split the video at the marked cut points."""
        if not self.current_video_path:
            return

        self.media_player.stop()
        self.media_player.setMedia(QMediaContent())

        try:
            from moviepy.editor import VideoFileClip

            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(self.current_video_path))[0]

            with VideoFileClip(self.current_video_path) as clip:
                times = [0] + [pt[0] for pt in self.cut_points] + [clip.duration]
                output_folder = "output"

                os.makedirs(output_folder, exist_ok=True)

                for i in range(len(times) - 1):
                    start = times[i]
                    end = times[i + 1]
                    if end <= start + 0.1:  # Minimum 0.1s duration
                        continue

                    subclip = clip.subclip(start, end)
                    # Use original filename with segment number
                    output_filename = os.path.join(
                        output_folder,
                        f"{base_name}_{i + 1}.mp4"
                    )
                    subclip.write_videofile(
                        output_filename,
                        codec="libx264",
                        audio_codec=None,
                        threads=4,
                        preset="ultrafast",
                        logger=None
                    )
                    subclip.close()

            print("Video cuts completed.")
        except Exception as e:
            print(f"Error during video processing: {str(e)}")
        finally:
            if self.current_video_path:
                url = QUrl.fromLocalFile(self.current_video_path)
                self.media_player.setMedia(QMediaContent(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Optionally set a global font that supports emoji better:
    app.setFont(QFont("Segoe UI Emoji", 10))

    window = VideoEditor()
    window.show()
    sys.exit(app.exec_())
