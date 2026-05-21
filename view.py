from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtUiTools import QUiLoader

class PipWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video PiP")
        self.resize(320, 240)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_label)

    def update_image(self, pixmap):
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

class MainView(QMainWindow):
    # Custom Signals to notify the Presenter
    pip_toggled = Signal()
    video_control_toggled = Signal()
    navigation_requested = Signal(int)  # Sends the page index
    mapping_requested = Signal(object)  # Sends the button object
    gesture_selected = Signal(str)      # Sends the gesture string
    stop_reading_score = Signal()

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("prueba.ui", None) 
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Gesture Control - MVP Architecture")
        self.resize(1020, 751)

        self.pip_window = None
        self._connect_signals()

    def _connect_signals(self):
        """Connects UI events to our custom Signals."""
        # Video controls
        self.ui.pipButton.clicked.connect(self.pip_toggled.emit)
        self.ui.stopButton.clicked.connect(self.video_control_toggled.emit)
        
        # Navigation
        self.ui.changeControlsButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.navigation_requested.emit(0))
        self.ui.gesturesBackButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.gesturesBackButton.clicked.connect(self.stop_reading_score.emit)
        
        # Gamepad Button Mapping Requests
        self.ui.A_button.clicked.connect(lambda: self.mapping_requested.emit(self.ui.A_button))
        self.ui.B_button.clicked.connect(lambda: self.mapping_requested.emit(self.ui.B_button))
        self.ui.Select_button.clicked.connect(lambda: self.mapping_requested.emit(self.ui.Select_button))
        self.ui.Start_button.clicked.connect(lambda: self.mapping_requested.emit(self.ui.Start_button))

        # Gesture Selection
        for btn in self.ui.buttonGroup.buttons():
            btn.clicked.connect(lambda checked=False, b=btn: self.gesture_selected.emit(b.property("gesture")))

    # --- PUBLIC METHODS FOR THE PRESENTER TO CONTROL THE UI ---

    def show_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

    def set_mapping_label(self, input_name, display_text):
        self.ui.buttonLabel.setProperty("button", input_name)
        self.ui.buttonLabel.setText(display_text)

    def click_gesture_button(self, gesture_name):
        """Clicks the corresponding UI button if a gesture is already mapped."""
        for btn in self.ui.buttonGroup.buttons():
            if btn.property("gesture") == gesture_name:
                btn.click()
                break

    def uncheck_all_gestures(self):
        checked_btn = self.ui.buttonGroup.checkedButton()
        if checked_btn:
            self.ui.buttonGroup.setExclusive(False)
            checked_btn.setChecked(False)
            self.ui.buttonGroup.setExclusive(True)

    def update_main_video(self, pixmap):
        self.ui.videoLabel.setPixmap(pixmap.scaled(
            self.ui.videoLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def update_score_bar(self, score_value, is_above_threshold):
        """Updates the progress bar value and changes color efficiently."""
        if self.ui.scoreBar.value() != score_value:
            self.ui.scoreBar.setValue(score_value)

        current_state = self.ui.scoreBar.property("is_above_threshold") or False
        
        if is_above_threshold and not current_state:
            self.ui.scoreBar.setStyleSheet("""
                QProgressBar { border: 1px solid #bcbcbc; border-radius: 5px; background-color: #e0e0e0; }
                QProgressBar::chunk { background-color: #FF5722; border-radius: 4px; }
            """)
            self.ui.scoreBar.setProperty("is_above_threshold", True)
            
        elif not is_above_threshold and current_state:
            self.ui.scoreBar.setStyleSheet("""
                QProgressBar { border: 1px solid #bcbcbc; border-radius: 5px; background-color: #e0e0e0; }
                QProgressBar::chunk { background-color: #0078D7; border-radius: 4px; }
            """)
            self.ui.scoreBar.setProperty("is_above_threshold", False)

    def get_slider_threshold(self):
        return self.ui.scoreSlider.value()

    # --- PIP WINDOW LOGIC ---
    def toggle_pip(self):
        if not self.pip_window:
            self.pip_window = PipWindow()
            self.pip_window.show()
            self.ui.videoLabel.setText("PiP Mode Active. Look at floating window.")
            self.ui.pipButton.setText("Return to Main UI")
            return True
        else:
            self.pip_window.close()
            self.pip_window = None
            self.ui.pipButton.setText("PiP Mode")
            return False

    def closeEvent(self, event):
        if self.pip_window:
            self.pip_window.close()
        event.accept()
    
    # --- STATUS BAR LOGIC ---
    def update_fps(self, fps):
        """Displays the current FPS in the window's bottom status bar."""
        self.ui.statusbar.showMessage(f"Estabilidad del Sistema: {fps} FPS")