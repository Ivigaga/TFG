import os
import subprocess
import string
import cv2
import time
import vgamepad as vg
from PySide6.QtCore import QObject, Qt, QCoreApplication, QEvent
from PySide6.QtGui import QImage, QPixmap,QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea
import math

class MainPresenter(QObject):
    def __init__(self, view, model, vision_engine):
        super().__init__()
        self.view = view
        self.model = model
        self.vision = vision_engine
        
        self.gamepad = vg.VX360Gamepad()
        
        # Mapeo exacto que tenías en CameraController.py
        self.buttons_map = {
            "XUSB_GAMEPAD_B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "XUSB_GAMEPAD_START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "XUSB_GAMEPAD_BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "XUSB_GAMEPAD_A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "XUSB_GAMEPAD_Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "XUSB_GAMEPAD_X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "XUSB_GAMEPAD_L1": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "XUSB_GAMEPAD_R1": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "XUSB_GAMEPAD_L2": "TRIGGER_L",
            "XUSB_GAMEPAD_R2": "TRIGGER_R"
        }

        self.platform_buttons={
            "Game Boy": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START"],
            "Game Boy Color": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START"],
            "Game Boy Advance": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_Y", "XUSB_GAMEPAD_X", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START", "XUSB_GAMEPAD_L1", "XUSB_GAMEPAD_R1"],
            "SNES": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_Y", "XUSB_GAMEPAD_X", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START", "XUSB_GAMEPAD_L1", "XUSB_GAMEPAD_R1"],
            "NES": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_START", "XUSB_GAMEPAD_BACK"],
            "Nintendo DS": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_Y", "XUSB_GAMEPAD_X", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START", "XUSB_GAMEPAD_L1", "XUSB_GAMEPAD_R1"],
            "Steam": ["XUSB_GAMEPAD_A", "XUSB_GAMEPAD_B", "XUSB_GAMEPAD_Y", "XUSB_GAMEPAD_X", "XUSB_GAMEPAD_BACK", "XUSB_GAMEPAD_START", "XUSB_GAMEPAD_L1", "XUSB_GAMEPAD_R1", "XUSB_GAMEPAD_L2", "XUSB_GAMEPAD_R2"]
        }
        
        # State variables
        self.is_reading_score = False
        self.current_mapped_gesture = None
        self.last_ui_update_time = 0
        
        # FPS Control variables
        self.fps_counter = 0
        self.last_fps_time = time.perf_counter()
        
        # Navigation Cooldown variables
        self.last_nav_time = 0.0
        self.nav_cooldown = 0.4  # Seconds between jumps (adjust to your liking, 0.4 is a good start)
        
        # Nueva variable para sustituir al QTimer
        self.is_video_playing = False 
        
        self._connect_view_signals()
        
        # CONEXIÓN MÁGICA: Conectamos la Señal del QThread con nuestro método
        self.vision.frame_processed.connect(self._on_frame_processed)
        
        # Arrancamos el hilo
        self.start_video()

        self.current_explorer_path = os.path.expanduser('~') # Empieza en la carpeta del usuario (C:\Users\...)
        self.explorer_mode = "FOLDER" 
        self.current_setup_console = None
        self.explorer_page_return_index = 8
        self.handle_platforms_screen_requested() # Prepara la pantalla de plataformas desde el inicio para evitar retrasos al abrirla por primera vez

        self.current_platform = None # Variable para almacenar la plataforma seleccionada en el catálogo de juegos
        self.handle_selected_navigation_mode(self.model.input_structure.get("noseLeft", {}).get("d-pad", False)) # Variable para controlar el modo de navegación (Joystick vs D-Pad)


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

        self.view.emulator_settings_opened.connect(self.handle_emulator_settings_opened)
        self.view.emulator_setup_requested.connect(self.handle_emulator_setup_requested)
        self.view.emulator_exe_chosen.connect(self.handle_emulator_exe_chosen)
        self.view.explorer_cancel_clicked.connect(self.handle_explorer_cancel)

        # Conexión para cuando el usuario hace clic en "Steam" o "NES"
        self.view.platform_selected.connect(self.handle_platform_selected)

        self.view.remove_platform.connect(self.handle_remove_platform)

        self.view.controls_opened.connect(self.handle_controls_opened)
        self.view.controls_closed.connect(self.handle_controls_closed)

        self.view.navigation_settings_opened.connect(self.handle_navigation_settings_opened)
        self.view.save_navigation_requested.connect(self.handle_save_navigation)

        self.view.selectedNavigationMode.connect(self.handle_selected_navigation_mode)
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
        # If the video is paused from the UI, ignore the frame
        if not self.is_video_playing:
            return

        # ==========================================
        # BLOCK 1: CORE LOGIC (Limited by TARGET_FPS)
        # ==========================================
        if is_new_processing:
            self.model.update_gesture_scores(blendshapes)
            self._process_gamepad_logic(landmarks)

            self.fps_counter += 1
            current_time = time.perf_counter()
            
            if (current_time - self.last_fps_time) >= 1.0:
                real_fps = int(self.fps_counter / (current_time - self.last_fps_time))
                self.view.update_fps(real_fps)
                self.fps_counter = 0
                self.last_fps_time = current_time

        # ==========================================
        # BLOCK 2: UI LOGIC (Maximum speed)
        # ==========================================
        current_time = time.perf_counter()

        # --- NUEVO: Actualización de los sliders de navegación ---
        if self.view.ui.stackedWidget.currentWidget().objectName() == "navigationPage":
            if (current_time - self.last_ui_update_time) >= 0.05: 
                if landmarks:
                    nose = landmarks[1]
                    # Al hacer (1.0 - valor), invertimos la dirección de la barra azul.
                    # Ahora, al mover la cabeza arriba o a la izquierda, la barra irá a la derecha.
                    ui_x = int((1.0 - nose.x) * 100)
                    ui_y = int((1.0 - nose.y) * 100)
                    self.view.update_navigation_sliders(ui_x, ui_y)
                self.last_ui_update_time = current_time

        # --- Actualización de la barra del catálogo de gestos ---
        elif self.is_reading_score and self.current_mapped_gesture:
            if (current_time - self.last_ui_update_time) >= 0.1:
                score = self.model.get_score(self.current_mapped_gesture)
                score_int = int(score * 100)
                threshold = self.view.get_slider_threshold()
                
                self.view.update_score_bar(score_int, score_int >= threshold)
                self.last_ui_update_time = current_time

        # Convert frame to QPixmap
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_frame.shape
        qt_img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # ==========================================
        # BLOCK 3: HUD DATA PREPARATION (Active inputs & Movement)
        # ==========================================
        target_buttons = self.platform_buttons.get(self.current_platform, [])
        

        # 1. Initialize all platform buttons as inactive (False) by default
        input_states = {btn: False for btn in target_buttons}

        # 2. Iterate through gestures to see if any mapped button is currently active
        for gesture_name, gesture_data in self.model.input_structure.items():
            btn_code = gesture_data.get("input")
            # If the mapped button belongs to the current platform
            if btn_code in input_states:
                # We use 'or' so if multiple gestures map to the same button, 
                # it stays True if at least one is active.
                input_states[btn_code] = input_states[btn_code] or gesture_data.get("active", False)

        # Get movement direction
        movement_direction = self._calculate_movement_direction()

        # ==========================================
        # BLOCK 4: UPDATE VIEW
        # ==========================================
        self.view.update_main_video(pixmap, input_states, movement_direction, self.current_platform, self.using_dPad)

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
            action_code = data.get("input")

            if score > threshold:
                    # THE USER JUST EXCEEDED THE THRESHOLD
                    
                    self._execute_press_action(data)
                    self.model.input_structure[gesture_name]["active"] = True
                        
            else:
                if is_currently_active:
                    # THE USER DROPPED BELOW THE THRESHOLD
                    
                    self._execute_release_action(data)
                    self.model.input_structure[gesture_name]["active"] = False

        # 2. EVALUAR JOYSTICK (Movimiento de la nariz)
        if landmarks:
            # En MediaPipe, el índice 1 corresponde a la punta de la nariz
            nose = landmarks[1]

            jx, jy = 0, 0
            
            # --- CORRECCIÓN: Separamos las direcciones ---
            is_left, is_right, is_up, is_down = False, False, False, False

            # Obtenemos los umbrales configurados
            th_left = inputs.get("noseLeft", {}).get("threshold", 0.6)
            th_right = inputs.get("noseRight", {}).get("threshold", 0.4)
            th_up = inputs.get("noseUp", {}).get("threshold", 0.4)
            th_down = inputs.get("noseDown", {}).get("threshold", 0.6)

            # Eje X
            if nose.x > th_left:
                jx = -20000
                is_left = True
            elif nose.x < th_right:
                jx = 20000
                is_right = True

            # Eje Y
            if nose.y > th_down:
                jy = -20000
                is_down = True
            elif nose.y < th_up:
                jy = 20000
                is_up = True

            # Control de modo continuo vs pasos 
            if not self.model.is_continuous_mode and (inputs.get("noseUp", {}).get("active") or inputs.get("noseDown", {}).get("active")):
                jy = 0
            if not self.model.is_continuous_mode and (inputs.get("noseLeft", {}).get("active") or inputs.get("noseRight", {}).get("active")):
                jx = 0

            if jx == 20000:
                self.navigate_interface("RIGHT") 
                if(self.using_dPad):
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            
            elif jx == -20000:
                self.navigate_interface("LEFT")  
                if(self.using_dPad):
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            else:
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            if jy == 20000:
                self.navigate_interface("UP")
                if(self.using_dPad):
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            elif jy == -20000:
                self.navigate_interface("DOWN")  
                if(self.using_dPad):
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            else:
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)  
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

            # --- CORRECCIÓN: Asignamos el estado exacto de cada dirección al modelo ---
            if "noseLeft" in inputs: inputs["noseLeft"]["active"] = is_left
            if "noseRight" in inputs: inputs["noseRight"]["active"] = is_right
            if "noseUp" in inputs: inputs["noseUp"]["active"] = is_up
            if "noseDown" in inputs: inputs["noseDown"]["active"] = is_down

            

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
        
        # 2. EXTRAER EL VALOR DEL D-PAD:
        # Asumimos que todos los gestos de nariz tienen el mismo ajuste de D-Pad.
        # Leemos el primer gesto de nariz que encontremos.
        new_dpad_mode = False # Valor por defecto

        new_dpad_mode = self.model.input_structure["noseLeft"].get("d-pad", False)

        # 3. Actualizar el estado interno y avisar a la lógica
        self.handle_selected_navigation_mode(new_dpad_mode)
        
        # 4. OPCIONAL: Actualizar los botones de la UI para que reflejen el modo cargado
        # Esto es vital para que el usuario sepa visualmente qué modo se ha cargado
        
        
        # 5. Volver al catálogo de gestos (Página 1)
        self.view.show_page(1)

    def handle_save_as_requested(self, filename):
        """El usuario ha escrito un nombre y pulsado guardar."""
        # 1. El modelo crea el JSON y guarda los datos de la memoria
        self.model.save_as_profile(filename)
        
        # 2. Volvemos al catálogo de gestos
        self.view.show_page(1)

    def handle_games_catalog_requested(self):
        """Solicita los juegos al modelo, ordena pintarlos y cambia a la pantalla de catálogo."""
        lista_juegos = self.obtain_current_platfor_games(self.current_platform)
        self.view.populate_games_catalog(lista_juegos, self.current_platform,self.model.emulators_config.get(self.current_platform))
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
            lista_actualizada = self.obtain_current_platfor_games(self.current_platform)
            self.view.populate_games_catalog(lista_actualizada, self.current_platform,self.model.emulators_config.get(self.current_platform))

    def handle_game_launch(self, exe_path):
        """Asynchronously launches the game executable, Steam URI, or ROM with its assigned emulator."""
        if not exe_path:
            print("Warning: This game does not have a valid execution path configured.")
            return

        # 1. Native executables or Steam shortcuts
        if exe_path.startswith("steam://") or exe_path.lower().endswith(".exe"):
            try:
                os.startfile(exe_path)
                print(f"Successfully launched: {exe_path}")
                # --- NEW: Minimize window after successful launch ---
                self.view.toggle_pip()
                self.view.showMinimized()
            except Exception as e:
                print(f"Critical error trying to open the game at '{exe_path}': {e}")
            return

        # 2. It's a ROM. Find its console and emulator.
        _, extension = os.path.splitext(exe_path)
        console_name = self.model.get_console_from_extension(extension)

        emulator_path = "Default"
        if console_name:
            emulator_path = self.model.emulators_config.get(console_name, "Default")

        try:
            # If set to Default, or the manually chosen .exe was deleted from the hard drive
            if emulator_path == "Default" or not os.path.exists(emulator_path):
                os.startfile(exe_path)
                print(f"Launching ROM with Windows Default: {exe_path}")
                # --- NEW: Minimize window after successful launch ---
                self.view.toggle_pip()
                self.view.showMinimized()
            else:
                # Launch the custom emulator, passing the ROM path as the main argument
                subprocess.Popen([emulator_path, exe_path])
                print(f"Launching ROM with custom emulator ({console_name}): {emulator_path} -> {exe_path}")
                # --- NEW: Minimize window after successful launch ---
                self.view.toggle_pip()
                self.view.showMinimized()
                
        except Exception as e:
            print(f"Critical error launching the ROM: {e}")

    def handle_explorer_opened(self):
        self.explorer_mode = "FOLDER"
        rutas_guardadas = self.model.get_rom_folders()
        
        if rutas_guardadas:
            self.current_explorer_path = rutas_guardadas[-1]
        else:

            self.current_explorer_path = os.path.expanduser('~')
            
        self.refresh_explorer()
        self.view.show_page(6)

    def refresh_explorer(self): # Hemos quitado el parámetro de aquí
        
        if self.current_explorer_path == "DRIVES":
            drives = [(f"{d}:\\", "folder") for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            self.view.populate_explorer("Este Equipo (Discos Duros)", drives, mode=self.explorer_mode)
            return

        try:
            items = os.listdir(self.current_explorer_path)
            
            # Always get folders
            folders = [f for f in items if os.path.isdir(os.path.join(self.current_explorer_path, f))]
            folders.sort(key=str.lower)
            content_list = [(f, "folder") for f in folders]
            
            # Inject .exe files ONLY if we are looking for an emulator
            if self.explorer_mode == "EMULATOR":
                exes = [f for f in items if f.lower().endswith('.exe')]
                exes.sort(key=str.lower)
                content_list.extend([(f, "exe") for f in exes])

            # USAMOS LA MEMORIA DE LA CLASE: self.explorer_page_return_index
            self.view.populate_explorer(self.current_explorer_path, content_list, mode=self.explorer_mode, page_index_return=self.explorer_page_return_index)
        except PermissionError:
            print(f"Acceso denegado a la carpeta: {self.current_explorer_path}")
            self.handle_explorer_up()

    def handle_explorer_select(self):
        """Action depends on the current explorer mode."""
        if self.explorer_mode == "FOLDER":
            self.view.ui.explorerSelectButton.setText("⏳ AÑADIENDO CARPETA...")
            self.view.ui.explorerSelectButton.setEnabled(False)
            
            self.model.add_rom_folder(self.current_explorer_path)
            
            lista_actualizada = self.obtain_current_platfor_games(self.current_platform)
            self.view.populate_games_catalog(lista_actualizada, self.current_platform, self.model.emulators_config.get(self.current_platform))
            
            self.view.ui.explorerSelectButton.setText("✅ ELEGIR ESTA CARPETA")
            self.view.ui.explorerSelectButton.setEnabled(True)
            if(self.current_platform != None):
                self.view.show_page(5)
            else:
                self.view.show_page(0)
            
        elif self.explorer_mode == "EMULATOR":
            # User clicked "PREDETERMINADO DE WINDOWS"
            if self.current_setup_console:
                self.model.emulators_config[self.current_setup_console] = "Default"
                self.model.save_emulators_config()
                
                # Refrescamos la pantalla de ajustes
                self.view.populate_emulator_settings(self.model.emulators_config)
                
                # --- FIX: Refrescar el botón del emulador si volvemos al catálogo ---
                if hasattr(self, 'explorer_page_return_index') and self.explorer_page_return_index == 5:
                    lista_juegos = self.obtain_current_platfor_games(self.current_platform)
                    self.view.populate_games_catalog(
                        lista_juegos, 
                        self.current_platform, 
                        self.model.emulators_config.get(self.current_platform)
                    )

                # Volvemos a la página que originó la petición usando la memoria
                if hasattr(self, 'explorer_page_return_index') and self.explorer_page_return_index is not None:
                    self.view.show_page(self.explorer_page_return_index)
                else:
                    self.view.show_page(8)

    def handle_explorer_cancel(self):
        """Returns to the correct page depending on where the explorer was launched from."""
        if self.explorer_mode == "FOLDER":
            # Si estábamos eligiendo carpeta de juegos, volvemos según la plataforma
            if self.current_platform != None:
                self.view.show_page(5)
            else:
                self.view.show_page(0)
                
        elif self.explorer_mode == "EMULATOR":
            # Usar la memoria de clase en lugar de forzar la página 8
            if hasattr(self, 'explorer_page_return_index') and self.explorer_page_return_index is not None:
                self.view.show_page(self.explorer_page_return_index)
            else:
                self.view.show_page(8)

    def handle_explorer_folder_clicked(self, folder_name):
 
        if self.current_explorer_path == "DRIVES":
            self.current_explorer_path = folder_name
            self.refresh_explorer()
            return

        new_path = os.path.join(self.current_explorer_path, folder_name)
        if os.path.isdir(new_path):
            self.current_explorer_path = new_path
            self.refresh_explorer()

    def handle_explorer_up(self):
        
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


    def navigate_interface(self, direction):
        """Navegación geométrica absoluta calculando coordenadas en pantalla."""

        if self.view.isMinimized():
            return
        
        if direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
            current_time = time.time()
            if current_time - self.last_nav_time < self.nav_cooldown:
                return  # Skip if the cooldown hasn't finished
            
            # If enough time has passed, update the timer and proceed to jump
            self.last_nav_time = current_time

        # 1. El gesto de "Aceptar" sigue inyectando un Enter normal
        if direction == "ENTER":
            current_widget = QApplication.focusWidget()
            if current_widget:
                # The most bulletproof way to trigger a button in Qt
                if hasattr(current_widget, "click"):
                    current_widget.click()
                else:
                    # Fallback for non-button widgets (Qt prefers Space over Return)
                    press_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Space, Qt.NoModifier)
                    release_event = QKeyEvent(QEvent.KeyRelease, Qt.Key_Space, Qt.NoModifier)
                    QCoreApplication.postEvent(current_widget, press_event)
                    QCoreApplication.postEvent(current_widget, release_event)
            return

        current_widget = QApplication.focusWidget()
        if not current_widget:
            return

        # 2. Obtenemos las coordenadas absolutas del botón actual en la pantalla
        centro_actual = current_widget.mapToGlobal(current_widget.rect().center())
        x1, y1 = centro_actual.x(), centro_actual.y()

        window = current_widget.window()
        best_candidate = None
        min_distance = float('inf')

        # 3. Scan ALL components in the current interface
        for candidate in window.findChildren(QWidget):
            if not candidate.isVisible() or not candidate.isEnabled() or candidate == current_widget:
                continue
            
            if candidate.focusPolicy() == Qt.NoFocus:
                continue

            # Candidate bounds (Bounding Box instead of just center)
            candidate_rect = candidate.rect()
            top_left = candidate.mapToGlobal(candidate_rect.topLeft())
            bottom_right = candidate.mapToGlobal(candidate_rect.bottomRight())
            
            # Centers are still used to determine the general direction (Left/Right/Up/Down)
            center_cand = candidate.mapToGlobal(candidate_rect.center())
            x2, y2 = center_cand.x(), center_cand.y()
            
            dx = x2 - x1
            dy = y2 - y1

            # --- FIX 1: Bounding Box Distance ---
            # If x1 is within the candidate's width, horizontal distance is 0
            dist_x = 0
            if x1 < top_left.x(): 
                dist_x = top_left.x() - x1
            elif x1 > bottom_right.x(): 
                dist_x = x1 - bottom_right.x()
            
            # If y1 is within the candidate's height, vertical distance is 0
            dist_y = 0
            if y1 < top_left.y(): 
                dist_y = top_left.y() - y1
            elif y1 > bottom_right.y(): 
                dist_y = y1 - bottom_right.y()

            is_valid = False
            distance = float('inf')

            # 4. Directional Filter with Penalty
            if direction == "RIGHT" and dx > 0:
                is_valid = True
                distance = math.hypot(dist_x, dist_y * 3) 
            elif direction == "LEFT" and dx < 0:
                is_valid = True
                distance = math.hypot(dist_x, dist_y * 3)
            elif direction == "DOWN" and dy > 0:
                is_valid = True
                distance = math.hypot(dist_x * 3, dist_y) 
            elif direction == "UP" and dy < 0:
                is_valid = True
                distance = math.hypot(dist_x * 3, dist_y)

            # 5. Save if it's the closest candidate
            if is_valid and distance < min_distance:
                min_distance = distance
                best_candidate = candidate

        # 6. Execute the focus jump
        if best_candidate:
            best_candidate.setFocus()

            # --- FIX 2: Auto-Scroll if the button is inside a scroll area ---
            
            parent = best_candidate.parentWidget()
            
            # Walk up the widget tree to see if we are inside a QScrollArea
            while parent:
                if isinstance(parent, QScrollArea):
                    # Ensure the widget is fully visible, adding a 10px padding for aesthetics
                    parent.ensureWidgetVisible(best_candidate, 10, 10)
                    break
                parent = parent.parentWidget()

    def _execute_press_action(self, input_data):
        """Acts as a router when a gesture exceeds the threshold."""
        action_code = input_data.get("input")
        if not action_code or action_code == "SYS_NONE":
            return
            
        # 1. Virtual gamepad button / Trigger
        if action_code.startswith("XUSB_"):
            if action_code == "XUSB_GAMEPAD_L2":
                self.gamepad.left_trigger_float(1.0)  # Presión al 100%
            elif action_code == "XUSB_GAMEPAD_R2":
                self.gamepad.right_trigger_float(1.0) # Presión al 100%
            else:
                # Botones normales (A, B, L1, Start...)
                self.gamepad.press_button(button=self.buttons_map[action_code])
            
        # 2. Internal system action
        elif action_code.startswith("SYS_"):
            if action_code == "SYS_CHANGE_MODE":
                self.model.is_continuous_mode = not self.model.is_continuous_mode
                                
            elif action_code == "SYS_NAV_ENTER":
                if not input_data.get("active", False):
                    self.navigate_interface("ENTER")
            
            elif action_code == "SYS_RESTORE_APP":
                if not input_data.get("active", False):
                    self.view.showNormal()
                    self.view.activateWindow()

    def _execute_release_action(self, input_data):
        """Releases the action when the user relaxes the gesture."""
        action_code = input_data.get("input")
        if not action_code or action_code == "SYS_NONE":
            return
            
        if action_code.startswith("XUSB_"):
            if action_code == "XUSB_GAMEPAD_L2":
                self.gamepad.left_trigger_float(value_float=0.0)
            elif action_code == "XUSB_GAMEPAD_R2":
                self.gamepad.right_trigger_float(value_float=0.0)
            else:
                # Botones normales (A, B, L1, Start...)
                self.gamepad.release_button(button=self.buttons_map[action_code])


    def handle_emulator_settings_opened(self):
        self.view.populate_emulator_settings(self.model.emulators_config)
        self.view.show_page(8)

    def handle_emulator_setup_requested(self, console_name, page_index_return):
        """Prepares the explorer to pick an executable for a specific console."""
        self.current_setup_console = console_name
        self.explorer_mode = "EMULATOR"
        
        # GUARDAMOS EL ÍNDICE EN LA MEMORIA DEL PRESENTER
        self.explorer_page_return_index = page_index_return

        self.current_explorer_path = os.path.expanduser('~')
        self.refresh_explorer() # Ya no pasamos el parámetro por aquí
        self.view.show_page(6)

    def handle_emulator_exe_chosen(self, filename, page_index_return=None):
        """Fired when an .exe is clicked in the explorer."""
        exe_path = os.path.join(self.current_explorer_path, filename)
        
        if self.current_setup_console:
            # 1. Guardamos la nueva ruta del emulador en el modelo y disco
            self.model.emulators_config[self.current_setup_console] = exe_path
            self.model.save_emulators_config()
            
            # 2. Refrescamos la pantalla de ajustes de emuladores (Página 8)
            self.view.populate_emulator_settings(self.model.emulators_config)
            
            # 3. FIX: Si volvemos a la pantalla del catálogo de juegos (Página 5),
            # recalculamos la lista y forzamos el repintado para actualizar el botón del emulador.
            if page_index_return == 5:
                lista_juegos = self.obtain_current_platfor_games(self.current_platform)
                self.view.populate_games_catalog(
                    lista_juegos, 
                    self.current_platform, 
                    self.model.emulators_config.get(self.current_platform)
                )
            
            # 4. Cambiamos a la pantalla que originó la petición
            if page_index_return is not None:
                self.view.show_page(page_index_return)
            else:
                self.view.show_page(8)


    def handle_platforms_screen_requested(self):
        """Prepara la lista de plataformas y ordena a la vista que las dibuje."""
        
        # 1. Sacamos los nombres de todas las consolas que tu modelo soporta
        # (NES, SNES, PlayStation 2, etc.)
        consolas = list(self.model.emulators_config.keys())
        
        # 2. Forzamos a que "Steam" sea el primer elemento de la lista
        lista_plataformas = ["Steam"] + consolas
        
        # 3. Mandamos los datos a la vista para que pinte los botones
        self.view.populate_platforms_catalog(lista_plataformas)
        
        # 4. Cambiamos a la nueva pantalla (sustituye el 9 por el índice de tu nueva página)
        self.view.show_page(0)

    def handle_platform_selected(self, platform_name):
        """Filtra la base de datos por consola y ordena mostrar el catálogo."""
        self.current_platform = platform_name
        # 1. Obtenemos absolutamente todos los juegos
        juegos_filtrados = self.obtain_current_platfor_games(platform_name)
        

        # 3. Ordenamos a la vista que dibuje SÓLO esta lista recortada
        self.view.populate_games_catalog(juegos_filtrados, platform_name,self.model.emulators_config.get(self.current_platform))
        
        # 4. Viajamos a la página 5 del catálogo de juegos
        self.view.show_page(5)


    def obtain_current_platfor_games(self, platform_name):
        lista_completa = self.model.get_installed_games()
        juegos_filtrados = []

        if(platform_name == None):
            return juegos_filtrados
 
        if platform_name == "Steam":
            # Los juegos de Steam se identifican porque su ruta empieza por steam://
            juegos_filtrados = [j for j in lista_completa if j.get("exe_path", "").startswith("steam://")]
        else:
            # Para el resto, miramos la extensión del archivo
            for juego in lista_completa:
                ruta = juego.get("exe_path", "")
                
                # Ignoramos los de Steam en esta pasada
                if not ruta.startswith("steam://"):
                    _, extension = os.path.splitext(ruta)
                    
                    # Le preguntamos al modelo a qué consola pertenece este archivo (.nes -> NES)
                    consola_del_juego = self.model.get_console_from_extension(extension)
                    
                    if consola_del_juego == platform_name:
                        juegos_filtrados.append(juego)
        return juegos_filtrados
    

    def handle_remove_platform(self):
        """Cuando el usuario pulsa el botón de volver desde el catálogo, eliminamos el filtro de plataforma para mostrar todo."""
        self.current_platform = None
        self.view.show_page(0)

    
    def handle_controls_opened(self):
        """Se ejecuta al pulsar 'Controles'. Elige la imagen y muestra la página."""
        # 1. El presentador recupera los datos del modelo
        gestos_maestros = self.model.get_available_gestures_metadata()
        
        # 2. Se los inyecta a la vista directamente antes de mostrar la página
        self.view.populate_gesture_catalog(gestos_maestros)

        # 3. El if-else para elegir la imagen según la plataforma actual
        if self.current_platform != None:
            if self.current_platform == "Game Boy":
                ruta_imagen = "images/controlGB.png"
            elif self.current_platform == "Game Boy Color":
                ruta_imagen = "images/controlGBC.png"
            elif self.current_platform == "Game Boy Advance":
                ruta_imagen = "images/controlGBA.png"
            elif self.current_platform == "Nintendo DS":
                ruta_imagen = "images/controlNDS.png"
            elif self.current_platform == "SNES":
                ruta_imagen = "images/controlSNES.png"
            elif self.current_platform == "NES":
                ruta_imagen = "images/controlNES.png"
            else:
                # Placeholder genérico para Steam, Nintendo DS, etc.
                ruta_imagen = "images/controlSteam.png"
            
            # 4. Ordenamos a la vista que ponga la imagen
            self.view.show_controller_image(ruta_imagen)
        
        # 5. Viajamos a la página de Gestos (Página 1)
        self.view.show_page(1)

    def handle_controls_closed(self):
        """Se ejecuta al pulsar 'Volver' en la pantalla de Gestos."""
        
        # 1. Ocultamos la imagen para que no moleste en el resto de la app
        self.view.hide_controller_image()
        
        # 2. Volvemos al menú principal / catálogo (Sustituye el 0 por el índice que necesites)
        self.view.show_page(0)

    def _calculate_movement_direction(self):
        """Returns the current active direction based on nose tracking."""
        inputs = self.model.input_structure
        
        up = inputs.get("noseUp", {}).get("active", False)
        down = inputs.get("noseDown", {}).get("active", False)
        left = inputs.get("noseLeft", {}).get("active", False)
        right = inputs.get("noseRight", {}).get("active", False)
        
        # Diagonal movements
        if up and right: return "NE"
        if up and left: return "NW"
        if down and right: return "SE"
        if down and left: return "SW"
        
        # Cardinal movements
        if up: return "N"
        if down: return "S"
        if left: return "W"
        if right: return "E"
        
        return "IDLE"
    

    def handle_navigation_settings_opened(self):
        """Lee los datos del modelo, los invierte visualmente y abre la pantalla."""
        inputs = self.model.input_structure
        
        # 1. Leemos los valores crudos del modelo (0.0 a 1.0)
        th_left = inputs.get("noseLeft", {}).get("threshold", 0.6)
        th_right = inputs.get("noseRight", {}).get("threshold", 0.4)
        th_up = inputs.get("noseUp", {}).get("threshold", 0.4)
        th_down = inputs.get("noseDown", {}).get("threshold", 0.6)

        # 2. Invertimos la matemática: (100 - (valor * 100)) para que encaje con la interfaz
        # (El threshold 'left' alimenta el low_thumb del slider x, etc.)
        low_x = int(100 - (th_left * 100))
        high_x = int(100 - (th_right * 100))
        
        low_y = int(100 - (th_down * 100))
        high_y = int(100 - (th_up * 100))
        
        # 3. Mandamos los datos a la vista y cambiamos de pantalla
        self.view.set_navigation_thumbs(low_x, high_x, low_y, high_y)
        self.view.show_page(self.view.ui.stackedWidget.indexOf(self.view.ui.navigationPage))

    def handle_save_navigation(self, low_x, high_x, low_y, high_y):
        """Guarda los valores de los sliders únicamente en la memoria RAM."""
        inputs = self.model.input_structure
        
        # Des-invertimos para volver al estándar de MediaPipe: (100 - valor_ui) / 100.0
        inputs["noseLeft"]["threshold"] = (100 - low_x) / 100.0
        inputs["noseLeft"]["d-pad"] = self.using_dPad
        inputs["noseRight"]["threshold"] = (100 - high_x) / 100.0
        inputs["noseRight"]["d-pad"] = self.using_dPad
        
        inputs["noseDown"]["threshold"] = (100 - low_y) / 100.0
        inputs["noseDown"]["d-pad"] = self.using_dPad
        inputs["noseUp"]["threshold"] = (100 - high_y) / 100.0
        inputs["noseUp"]["d-pad"] = self.using_dPad

        # NOTA: Eliminamos la escritura a disco aquí. Los valores se mantienen 
        # modificados en memoria listos para cuando se pulse guardar en la pantalla de gestos.
        
        # Volvemos a la página de Gestos
        self.view.show_page(self.view.ui.stackedWidget.indexOf(self.view.ui.gesturesPage))

    def handle_selected_navigation_mode(self, mode):
        self.using_dPad = mode

        if hasattr(self.view.ui, 'btn_nav_joystick') and hasattr(self.view.ui, 'btn_nav_dpad'):
            self.view.ui.btn_nav_dpad.setChecked(mode)
            self.view.ui.btn_nav_joystick.setChecked(not mode)