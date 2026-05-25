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
    gesture_selected = Signal(object)      # Sends the gesture button object
    stop_reading_score = Signal()
    save_controls = Signal(str, str, int)  # gesture_code, input_code, threshold

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
        self.ui.controlsCancelButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))
        self.ui.controlsCancelButton.clicked.connect(self.stop_reading_score.emit)
        self.ui.gesturesBackButton.clicked.connect(lambda: self.navigation_requested.emit(0))
        
        

        # --- NAVEGACIÓN ANIDADA DE ACCIONES ---
        self.ui.btn_cat_mando.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(1))
        self.ui.btn_cat_sys.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(2))
        self.ui.btn_volver_cat1.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))
        self.ui.btn_volver_cat2.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))

        # Botón Guardar (Por ahora solo hace navegación de vuelta al catálogo)
        self.ui.controlsSaveButon.clicked.connect(lambda: self.save_controls.emit(self.get_selected_gesture(),self.get_selected_control(),self.get_slider_threshold()))
        self.ui.controlsSaveButon.clicked.connect(self.stop_reading_score.emit)

        # Botón Limpiar/Deseleccionar
        self.ui.controlsCleanButton.clicked.connect(self.clear_selection)

        # Gesture Selection
        for btn in self.ui.gestureButtons.buttons():
            btn.clicked.connect(lambda checked=False, b=btn: self.gesture_selected.emit(b))
        
        # Escuchar clics en las opciones para iluminar la categoría en tiempo real
        self.ui.controlButtons.buttonClicked.connect(self._on_action_button_clicked)

        # --- CONTROL DINÁMICO DEL SLIDER Y UMBRALES ---
        # Sincronizar el texto informativo con el valor real del slider
        self.ui.scoreSlider.valueChanged.connect(self._on_slider_value_changed)
        
        # Hacer que los botones masivos incrementen o decrementen el slider
        self.ui.btn_plus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() + 5))
        self.ui.btn_minus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() - 5))

    # --- PUBLIC METHODS FOR THE PRESENTER TO CONTROL THE UI ---

    def show_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

    def set_mapping_label(self,gesture_code, gesture_name):
        self.ui.gestureLabel.setProperty("gesture", gesture_code)
        self.ui.gestureLabel.setText(gesture_name)

    def click_gesture_button(self, gesture_name):
        """Clicks the corresponding UI button if a gesture is already mapped."""
        for btn in self.ui.buttonGroup.buttons():
            if btn.property("gesture") == gesture_name:
                btn.click()
                break
    def click_input_button(self, input_name):
        """Clicks the corresponding UI button if an input is already mapped."""
        for btn in self.ui.controlButtons.buttons():
            if btn.property("gamepadInput") == input_name:
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
            self.ui.scoreBar.setProperty("is_above_threshold", True)
            self.ui.scoreBar.style().unpolish(self.ui.scoreBar)
            self.ui.scoreBar.style().polish(self.ui.scoreBar)
            
        elif not is_above_threshold and current_state:
            self.ui.scoreBar.setProperty("is_above_threshold", False)
            self.ui.scoreBar.style().unpolish(self.ui.scoreBar)
            self.ui.scoreBar.style().polish(self.ui.scoreBar)

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

    def _on_action_button_clicked(self, button):
        """Detects which option was clicked and highlights its parent category."""
        input_code = button.property("gamepadInput")
        if input_code:
            if input_code.startswith("XUSB"):
                self.highlight_category("gamepad")
            elif input_code.startswith("SYS"):
                self.highlight_category("system")

    def highlight_category(self, category_type):
        """Highlights the correct category button and unhighlights the other."""
        # Aplicamos la propiedad dinámica booleana
        self.ui.btn_cat_mando.setProperty("active_category", category_type == "gamepad")
        self.ui.btn_cat_sys.setProperty("active_category", category_type == "system")
        
        # Forzamos a Qt a repintar los botones con la nueva regla QSS
        for btn in [self.ui.btn_cat_mando, self.ui.btn_cat_sys]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def get_selected_control(self):
        """Returns the gamepad input code of the currently selected control button."""
        checked_btn = self.ui.controlButtons.checkedButton()
        if checked_btn:
            return checked_btn.property("gamepadInput")
        return None
    
    def get_selected_gesture(self):
        """Returns the gesture code of the currently selected gesture"""
        return self.ui.gestureLabel.property("gesture")

    def clear_selection(self):
        """Deselects any selected action and removes category highlights."""
        # 1. Desmarcar cualquier botón de acción (A, B, Start, Cambiar Modo...)
        checked_btn = self.ui.controlButtons.checkedButton()
        if checked_btn:
            # En Qt, para desmarcar un botón de un grupo exclusivo por código,
            # hay que apagar la exclusividad temporalmente.
            self.ui.controlButtons.setExclusive(False)
            checked_btn.setChecked(False)
            self.ui.controlButtons.setExclusive(True)
            
        # 2. Apagar el borde azul de las categorías (Mando / Sistema)
        self.ui.btn_cat_mando.setProperty("active_category", False)
        self.ui.btn_cat_sys.setProperty("active_category", False)
        
        # 3. Obligar a Qt a repintar las categorías para que desaparezca el borde
        for btn in [self.ui.btn_cat_mando, self.ui.btn_cat_sys]:
            btn.style().unpolish(btn)
            btn.style().polish(btn)


    def _on_slider_value_changed(self, value):
        """Actualiza el texto informativo cada vez que cambia el slider."""
        self.ui.info_calib.setText(f"Umbral actual: {value}%")

    def set_slider_threshold(self, value):
        """Establece el valor numérico del slider al cargar la pantalla."""
        self.ui.scoreSlider.setValue(value)
        self.ui.info_calib.setText(f"Umbral actual: {value}%")