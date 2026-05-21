import cv2
import time
import vgamepad as vg
from PySide6.QtCore import QTimer, QObject
from PySide6.QtGui import QImage, QPixmap

class MainPresenter(QObject):
    def __init__(self, view, model, vision_engine):
        super().__init__()
        self.view = view
        self.model = model
        self.vision = vision_engine
        
        self.gamepad = vg.VX360Gamepad()
        
        # State variables
        self.is_reading_score = False
        self.current_mapped_gesture = None
        self.last_ui_update_time = 0
        
        # FPS Control variables
        self.fps_counter = 0
        self.last_fps_time = time.perf_counter()
        
        self._connect_view_signals()
        
        # Configure Main Loop (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._main_loop)
        self.start_video()

    def _connect_view_signals(self):
        """Binds View signals to Presenter logic."""
        self.view.pip_toggled.connect(self.view.toggle_pip)
        self.view.video_control_toggled.connect(self.toggle_video)
        self.view.navigation_requested.connect(self.view.show_page)
        
        self.view.mapping_requested.connect(self.handle_mapping_request)
        self.view.gesture_selected.connect(self.handle_gesture_selection)
        self.view.stop_reading_score.connect(self.stop_reading)

    # --- PRESENTER LOGIC ---

    def start_video(self):
        self.timer.start(16) # ~60 FPS
        self.view.ui.stopButton.setText("Pause Video")

    def stop_video(self):
        self.timer.stop()
        self.view.ui.stopButton.setText("Resume Video")

    def toggle_video(self):
        if self.timer.isActive():
            self.stop_video()
        else:
            self.start_video()

    def stop_reading(self):
        self.is_reading_score = False

    def handle_mapping_request(self, button_obj):
        """Fired when user wants to map a gamepad button (A, B, Start...)."""
        input_id = button_obj.property("gamepadInput")
        self.view.set_mapping_label(input_id, button_obj.text())
        
        # Reset View State
        self.view.ui.scoreBar.setValue(0)
        self.view.uncheck_all_gestures()
        
        # Enable reading and check if previously mapped
        self.is_reading_score = True
        self.current_mapped_gesture = None
        
        mapped_gesture = self.model.get_gesture_by_input(input_id)
        if mapped_gesture:
            self.view.click_gesture_button(mapped_gesture)
            
        self.view.show_page(2)

    def handle_gesture_selection(self, gesture_name):
        """Fired when user clicks 'Smile', 'Blink', etc."""
        self.current_mapped_gesture = gesture_name
        self.is_reading_score = True

    # --- MAIN LOOP ---

    def _main_loop(self):
        # 1. Desempaquetamos el cuarto valor (is_new_processing)
        frame, blendshapes, landmarks, is_new_processing = self.vision.get_processed_frame()
        if frame is None:
            return

        # ==========================================
        # BLOQUE 1: LÓGICA CORE (Limitada por TARGET_FPS)
        # ==========================================
        if is_new_processing:
            # Actualizamos el modelo y el mando SOLO si hay nuevos datos
            self.model.update_gesture_scores(blendshapes)
            self._process_gamepad_logic()

            # El contador de FPS ahora mide el cerebro de la IA, no la interfaz
            self.fps_counter += 1
            current_time = time.perf_counter()
            
            if (current_time - self.last_fps_time) >= 1.0:
                fps_reales = int(self.fps_counter / (current_time - self.last_fps_time))
                self.view.update_fps(fps_reales)
                
                self.fps_counter = 0
                self.last_fps_time = current_time

        # ==========================================
        # BLOQUE 2: LÓGICA DE INTERFAZ (Máxima velocidad)
        # ==========================================
        
        # View Update: Score Bar (at ~10 FPS)
        tiempo_actual = time.perf_counter()
        if self.is_reading_score and self.current_mapped_gesture:
            if (tiempo_actual - self.last_ui_update_time) >= 0.1:
                score = self.model.get_score(self.current_mapped_gesture)
                score_int = int(score * 100)
                threshold = self.view.get_slider_threshold()
                
                self.view.update_score_bar(score_int, score_int >= threshold)
                self.last_ui_update_time = tiempo_actual

        # View Update: Video Stream
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_frame.shape
        qt_img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        if self.view.pip_window and self.view.pip_window.isVisible():
            self.view.pip_window.update_image(pixmap)
        else:
            self.view.update_main_video(pixmap)

    def _process_gamepad_logic(self):
        """Evaluates thresholds and triggers vgamepad events."""
        # For MVP, we encapsulate hardware calls here based on model data.
        # Example for A button mapping (Blink Right):
        # In a real scenario, you iterate over self.model.input_structure
        self.gamepad.update()

    def shutdown(self):
        self.timer.stop()
        self.vision.release_resources()
        self.gamepad.reset()
        self.gamepad.update()