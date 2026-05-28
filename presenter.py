import os

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

        self.current_explorer_path = os.path.expanduser('~') # Empieza en la carpeta del usuario (C:\Users\...)

    def _connect_view_signals(self):
        """Binds View signals to Presenter logic."""
        self.view.pip_toggled.connect(self.view.toggle_pip)
        self.view.video_control_toggled.connect(self.toggle_video)
        self.view.navigation_requested.connect(self.view.show_page)
        
        self.view.gesture_selected.connect(self.handle_gesture_selection)
        self.view.stop_reading_score.connect(self.stop_reading)

        self.view.save_controls.connect(self.save_control_mapping)

        self.view.save_mapping_current.connect(self.save_control_mapping_current)

        self.view.load_profiles_requested.connect(self.handle_load_profiles_requested)
        self.view.profile_accepted.connect(self.handle_profile_accepted)

        self.view.save_as_requested.connect(self.handle_save_as_requested)

        self.view.games_catalog_requested.connect(self.handle_games_catalog_requested)
        self.view.scan_games_requested.connect(self.handle_scan_games)
        # Conexión para el lanzamiento de videojuegos
        self.view.game_launch_requested.connect(self.handle_game_launch)

        

        # Explorador
        self.view.explorer_opened.connect(self.handle_explorer_opened)
        self.view.explorer_folder_clicked.connect(self.handle_explorer_folder_clicked)
        self.view.explorer_up_clicked.connect(self.handle_explorer_up)
        self.view.explorer_select_clicked.connect(self.handle_explorer_select)

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

    def save_control_mapping_current(self):
        self.model.save_inputs()  # Guardamos el JSON con la configuración actual en memoria
        self.view.show_page(0)  # Volvemos a la página principal del catálogo de gestos

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

    def save_control_mapping(self, gesture_code, input_code, threshold):
        """Recibe la señal del botón Guardar en la UI, actualiza la memoria y vuelve al menú."""
        # 1. Ejecutamos la actualización en memoria
        self.model.save_control_mapping(gesture_code, input_code, threshold)
        
        # 2. Detenemos la actualización rápida de la barra de progreso
        self.is_reading_score = False
        self.current_mapped_gesture = None

        self.view.ui.stackedWidgetAcciones.setCurrentIndex(0)
        
        # 3. Ordenamos a la Vista que vuelva a la página 1 (El catálogo de gestos)
        self.view.show_page(1)

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
            
        # 3. Sincronizamos el Slider con el umbral actual guardado en el modelo
        gesture_data = self.model.input_structure.get(gesture_code, {})
        current_threshold = int(gesture_data.get("threshold", 0.5) * 100)
        self.view.set_slider_threshold(current_threshold)
            
        self.view.show_page(2)

    def handle_load_profiles_requested(self):
        """El usuario ha pulsado 'Cargar Archivo'."""
        # 1. Pedir al modelo los archivos disponibles
        profiles = self.model.get_available_profiles()
        
        # 2. Ordenar a la vista que los dibuje
        self.view.populate_profiles(profiles)
        
        # 3. Viajar a la Página 3 (La nueva pantalla de Cargar)
        self.view.show_page(3)
        
    def handle_profile_accepted(self, filename):
        """El usuario ha seleccionado un perfil y pulsado 'Aceptar'."""
        # 1. Cambiar el archivo en el modelo y recargar la RAM
        self.model.load_profile(filename)
        
        # 2. Volver al catálogo de gestos (Página 1)
        self.view.show_page(1)

    def handle_save_as_requested(self, filename):
        """El usuario ha escrito un nombre y pulsado guardar."""
        # 1. El modelo crea el JSON y guarda los datos de la memoria
        self.model.save_as_profile(filename)
        
        # 2. Volvemos al catálogo de gestos
        self.view.show_page(1)

    def handle_games_catalog_requested(self):
        """Solicita los juegos al modelo, ordena pintarlos y cambia a la pantalla de catálogo."""
        lista_juegos = self.model.get_installed_games()
        self.view.populate_games_catalog(lista_juegos)
        self.view.show_page(5) # Muestra la nueva gamesPage

    def handle_scan_games(self):
        """Ejecuta el escáner del modelo y recarga la vista si encuentra algo nuevo."""
        # 1. Cambiamos el texto temporalmente para dar feedback visual
        self.view.ui.gamesScanButton.setText("ESCANEANDO...")
        self.view.ui.gamesScanButton.setEnabled(False)
        
        # 2. Ejecutar la lógica de detección
        nuevos_encontrados = self.model.auto_detect_steam_games()
        
        # 3. Restaurar botón
        self.view.ui.gamesScanButton.setText("🔍 ESCANEAR STEAM")
        self.view.ui.gamesScanButton.setEnabled(True)
        
        # 4. Si ha encontrado juegos, repintamos la cuadrícula
        if nuevos_encontrados:
            lista_actualizada = self.model.get_installed_games()
            self.view.populate_games_catalog(lista_actualizada)

    def handle_game_launch(self, exe_path):
        """Lanza de forma asíncrona el ejecutable del juego o la URI de Steam."""
        if not exe_path:
            print("Advertencia: Este juego no tiene una ruta de ejecución válida configurada.")
            return

        import os
        try:
            # Justificación para el TFG: os.startfile delega la ejecución al núcleo de Windows.
            # Al ser no bloqueante (no espera a que el programa termine), la interfaz de Python
            # sigue respondiendo y procesando la cámara en segundo plano sin sufrir microtirones.
            os.startfile(exe_path)
            print(f"Lanzando con éxito: {exe_path}")
        except Exception as e:
            print(f"Error crítico al intentar abrir el juego en '{exe_path}': {e}")

    def handle_explorer_opened(self):
        """Abre el explorador de carpetas recordando la última ruta configurada."""
        rutas_guardadas = self.model.get_rom_folders()
        
        if rutas_guardadas:
            # Recuperamos el último elemento de la lista [-1]
            self.current_explorer_path = rutas_guardadas[-1]
        else:
            import os
            self.current_explorer_path = os.path.expanduser('~')
            
        self.refresh_explorer()
        self.view.show_page(6)

    def refresh_explorer(self):
        """Lee el disco duro o lista las unidades físicas si estamos en la vista general."""
        import os
        import string
        
        # --- NUEVO: Estado de "Este Equipo" ---
        if self.current_explorer_path == "DRIVES":
            # Escaneamos el abecedario buscando qué letras de disco existen realmente en tu Windows
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            self.view.populate_explorer("Este Equipo (Discos Duros)", drives)
            return

        try:
            items = os.listdir(self.current_explorer_path)
            folders = [f for f in items if os.path.isdir(os.path.join(self.current_explorer_path, f))]
            folders.sort(key=str.lower)
            self.view.populate_explorer(self.current_explorer_path, folders)
        except PermissionError:
            print(f"Acceso denegado a la carpeta: {self.current_explorer_path}")
            self.handle_explorer_up()

    def handle_explorer_folder_clicked(self, folder_name):
        import os
        
        # --- NUEVO: Si estamos eligiendo disco, saltamos directamente a él ---
        if self.current_explorer_path == "DRIVES":
            self.current_explorer_path = folder_name
            self.refresh_explorer()
            return

        new_path = os.path.join(self.current_explorer_path, folder_name)
        if os.path.isdir(new_path):
            self.current_explorer_path = new_path
            self.refresh_explorer()

    def handle_explorer_up(self):
        import os
        
        # Si ya estamos viendo los discos, no hay nada más arriba
        if self.current_explorer_path == "DRIVES":
            return

        padre = os.path.dirname(self.current_explorer_path)
        
        # --- NUEVO: Si el padre es igual a la ruta actual, hemos chocado con el techo (ej. C:\) ---
        if padre == self.current_explorer_path: 
            self.current_explorer_path = "DRIVES" # Activamos la vista de unidades
        else:
            self.current_explorer_path = padre
            
        self.refresh_explorer()

    def handle_explorer_select(self):
        """Registra la carpeta, borra la caché y actualiza el catálogo."""
        self.view.ui.explorerSelectButton.setText("⏳ AÑADIENDO CARPETA...")
        self.view.ui.explorerSelectButton.setEnabled(False)
        
        # 1. Al añadir la ruta, el modelo vacía la variable self._cached_roms por dentro
        self.model.add_rom_folder(self.current_explorer_path)
        
        # 2. Al pedir los juegos ahora, el modelo detecta que no hay caché y hace el barrido real
        lista_actualizada = self.model.get_installed_games()
        self.view.populate_games_catalog(lista_actualizada)
        
        self.view.ui.explorerSelectButton.setText("✅ ELEGIR ESTA CARPETA")
        self.view.ui.explorerSelectButton.setEnabled(True)
        
        self.view.show_page(5)