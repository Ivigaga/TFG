import cv2
import time
import vgamepad as vg
from PySide6.QtCore import QObject
from PySide6.QtGui import QImage, QPixmap

class MainPresenter(QObject):
    def __init__(self, view, model, vision_engine):
        super().__init__()
        self.view = view
        self.model = model
        self.vision = vision_engine
        
        self.gamepad = vg.VX360Gamepad()
        
        # Mapeo exacto que tenías en CameraController.py
        self.botones_map = {
            "XUSB_GAMEPAD_B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "XUSB_GAMEPAD_START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "XUSB_GAMEPAD_BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "XUSB_GAMEPAD_A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A
        }
        
        # State variables
        self.is_reading_score = False
        self.current_mapped_gesture = None
        self.last_ui_update_time = 0
        
        # FPS Control variables
        self.fps_counter = 0
        self.last_fps_time = time.perf_counter()
        
        # Nueva variable para sustituir al QTimer
        self.is_video_playing = False 
        
        self._connect_view_signals()
        
        # CONEXIÓN MÁGICA: Conectamos la Señal del QThread con nuestro método
        self.vision.frame_processed.connect(self._on_frame_processed)
        
        # Arrancamos el hilo
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
        self.is_video_playing = True
        
        # Si el hilo de la cámara no está corriendo, lo arrancamos
        if not self.vision.isRunning():
            self.vision.start()
            
        self.view.ui.stopButton.setText("Pause Video")

    def stop_video(self):
        # Al poner esto a False, _on_frame_processed ignorará los frames
        self.is_video_playing = False
        self.view.ui.stopButton.setText("Resume Video")

    def toggle_video(self):
        if self.is_video_playing:
            self.stop_video()
        else:
            self.start_video()

    def stop_reading(self):
        self.is_reading_score = False

    def handle_mapping_request(self, button_obj):
        """Fired when user wants to map a gamepad button (A, B, Start...)."""
        return
        input_id = button_obj.property("gamepadInput")
        self.view.set_mapping_label(input_id, button_obj.text())
        
        # Reset View State
        self.view.ui.scoreBar.setValue(0)
        self.view.uncheck_all_gestures()
        
        # Enable reading and check if previously mapped
        #self.is_reading_score = True
        #self.current_mapped_gesture = None
        
        mapped_gesture = self.model.get_gesture_by_input(input_id)
        if mapped_gesture:
            self.view.click_gesture_button(mapped_gesture)
            
        self.view.show_page(2)

    def handle_gesture_selection(self, gesture_button):
        """Fired when user clicks 'Smile', 'Blink', etc."""
        gesture_name = gesture_button.text()
        gesture_code = gesture_button.property("gesture")
        self.current_mapped_gesture = gesture_code
        self.view.set_mapping_label(gesture_code,gesture_name)
        self.is_reading_score = True
        gesture_input = self.model.get_input_from_gesture(gesture_code)
        if gesture_input:
            self.view.click_input_button(gesture_input)
            
        self.view.show_page(2)


    # --- MAIN LOOP ---

    def _on_frame_processed(self, frame, blendshapes, landmarks, is_new_processing):
        # Si hemos pausado el vídeo desde la interfaz, ignoramos el paquete
        if not self.is_video_playing:
            return

        # ==========================================
        # BLOQUE 1: LÓGICA CORE (Limitada por TARGET_FPS)
        # ==========================================
        if is_new_processing:
            self.model.update_gesture_scores(blendshapes)
            self._process_gamepad_logic(landmarks)

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
        tiempo_actual = time.perf_counter()
        if self.is_reading_score and self.current_mapped_gesture:
            if (tiempo_actual - self.last_ui_update_time) >= 0.1:
                score = self.model.get_score(self.current_mapped_gesture)
                score_int = int(score * 100)
                threshold = self.view.get_slider_threshold()
                
                self.view.update_score_bar(score_int, score_int >= threshold)
                self.last_ui_update_time = tiempo_actual

        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_frame.shape
        qt_img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        if self.view.pip_window and self.view.pip_window.isVisible():
            self.view.pip_window.update_image(pixmap)
        else:
            self.view.update_main_video(pixmap)

    def _process_gamepad_logic(self, landmarks):
        """Evaluates thresholds, triggers vgamepad events, and moves joysticks."""
        inputs = self.model.input_structure

        # 1. EVALUAR GESTOS (Botones y Modos)
        for gesture_name, data in inputs.items():
            # Saltamos los gestos de la nariz en este bucle, van por separado
            if gesture_name.startswith("nose"):
                continue

            score = data.get("score", 0.0)
            threshold = data.get("threshold", 0.5)
            is_currently_active = data.get("active", False)
            
            # Qué debe hacer este gesto (pushInputButton o changeMovementMode)
            funcion_asignada = data.get("function")
            button_name = data.get("input")

            if score > threshold:
                if not is_currently_active:
                    # EL USUARIO ACABA DE SUPERAR EL UMBRAL
                    self.model.input_structure[gesture_name]["active"] = True

                    if funcion_asignada == "pushInputButton" and button_name:
                        # Pulsar el botón físico
                        self.gamepad.press_button(button=self.botones_map[button_name])

                    elif funcion_asignada == "changeMovementMode":
                        # Cambiar el modo de movimiento del sistema
                        self.model.is_continuous_mode = not self.model.is_continuous_mode
                        
            else:
                if is_currently_active:
                    # EL USUARIO HA BAJADO DEL UMBRAL
                    self.model.input_structure[gesture_name]["active"] = False

                    if funcion_asignada == "pushInputButton" and button_name:
                        # Soltar el botón físico
                        self.gamepad.release_button(button=self.botones_map[button_name])

        # 2. EVALUAR JOYSTICK (Movimiento de la nariz)
        if landmarks:
            # En MediaPipe, el índice 1 corresponde a la punta de la nariz
            nose = landmarks[1]

            jx, jy = 0, 0
            movinx, moviny = False, False

            # Obtenemos los umbrales configurados
            th_left = inputs.get("noseLeft", {}).get("threshold", 0.6)
            th_right = inputs.get("noseRight", {}).get("threshold", 0.4)
            th_up = inputs.get("noseUp", {}).get("threshold", 0.4)
            th_down = inputs.get("noseDown", {}).get("threshold", 0.6)

            # Eje X
            if nose.x > th_left:
                jx = -20000
                movinx = True
            elif nose.x < th_right:
                jx = 20000
                movinx = True

            # Eje Y
            if nose.y > th_down:
                jy = -20000
                moviny = True
            elif nose.y < th_up:
                jy = 20000
                moviny = True

            # Control de modo continuo vs pasos (replicado de tu código original)
            if not self.model.is_continuous_mode and (inputs.get("noseUp", {}).get("active") or inputs.get("noseDown", {}).get("active")):
                jy = 0

            # Guardamos el estado de activación en el modelo por si se necesita
            if "noseLeft" in inputs: inputs["noseLeft"]["active"] = movinx
            if "noseRight" in inputs: inputs["noseRight"]["active"] = movinx
            if "noseUp" in inputs: inputs["noseUp"]["active"] = moviny
            if "noseDown" in inputs: inputs["noseDown"]["active"] = moviny

            # Mover el joystick izquierdo del mando de Xbox
            self.gamepad.left_joystick(x_value=jx, y_value=jy)

        # 3. ENVIAR SEÑAL AL DRIVER
        self.gamepad.update()

    def shutdown(self):
        # Ya no hay timer que detener, solo liberamos la cámara y el mando
        self.vision.release_resources()
        self.gamepad.reset()
        self.gamepad.update()
    
    def handle_gesture_selection(self, gesture_button):
        """Fired when user clicks 'Smile', 'Blink', etc."""
        gesture_name = gesture_button.text()
        gesture_code = gesture_button.property("gesture")
        
        self.current_mapped_gesture = gesture_code
        self.view.set_mapping_label(gesture_code, gesture_name)
        self.is_reading_score = True
        
        # 1. Leemos el tipo de categoría guardada en el JSON y la iluminamos
        gesture_type = self.model.get_type_from_gesture(gesture_code)
        self.view.highlight_category(gesture_type)
        
        # 2. Hacemos clic automático en la opción de la sub-pestaña si la hay
        gesture_input = self.model.get_input_from_gesture(gesture_code)
        if gesture_input:
            self.view.click_input_button(gesture_input)
            
        self.view.show_page(2)