"""
Módulo Presenter - Capa de Lógica de Negocio de la Arquitectura MVP

Responsabilidades principales:
  - Mediar la comunicación entre Vista (UI) y Modelo (datos/estado)
  - Procesar datos de reconocimiento de gestos faciales desde MediaPipe
  - Gestionar control virtual de mando Xbox 360 mediante vgamepad
  - Orquestar lanzamiento de juegos, gestión de perfiles y configuración
  - Manejar todos los eventos disparados por interacciones de usuario en la UI
  - Mapear gestos a entrada de mando con lógica de umbrales configurables
  - Implementar navegación direccional a través de la interfaz usando seguimiento facial
  - Gestionar el estado de la aplicación (plataforma actual, ruta del explorador, progreso tutorial)

Características principales:
  - Control de mando en tiempo real via emulación de Xbox 360
  - Monitoreo continuo de puntuación de gestos con umbrales configurables
  - Selección de modo de navegación D-Pad vs Joystick
  - Navegación inteligente de UI usando cálculos de proximidad geométrica
  - Sistema de guardar/cargar perfiles y configuración
  - Catálogo de juegos con soporte Steam + emuladores ROM
  - Sistema de tutorial para incorporación de nuevos usuarios
  - Monitoreo de FPS y gestión de velocidad de fotogramas
  - Control de enfriamiento para prevenir navegación rápida repetida
"""

import ctypes
import os
import subprocess
import string
import cv2
import time
import vgamepad as vg
from PySide6.QtCore import QObject, QTimer, Qt, QCoreApplication, QEvent
from PySide6.QtGui import QImage, QPixmap, QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget, QScrollArea
import math

class MainPresenter(QObject):
    """
    Capa de lógica de negocio implementando el componente Presenter de la arquitectura MVP.
    
    Gestiona el flujo central de la aplicación: recibir datos de gestos del motor de visión,
    actualizar el estado del modelo, emitir comandos de mando, y orquestar actualizaciones de la vista.
    Actúa como el centro coordinador conectando todos los componentes de la aplicación.
    """
    
    def __init__(self, view, model, vision_engine):
        """
        Inicializar el Presenter con referencias a Vista, Modelo y Motor de Visión.
        
        Args:
            view: Instancia de MainView - gestiona toda la renderización UI e interacción de usuario
            model: Instancia de Modelo - mantiene estado de aplicación, perfiles y configuración
            vision_engine: Procesador MediaPipe basado en QThread - proporciona landmarks faciales y puntuaciones de gestos
        
        Inicializa:
            - Emulación de mando Xbox 360 virtual (librería vgamepad)
            - Mapeo de códigos de botones desde nombres de gestos a códigos de mando
            - Configuraciones de botones específicas por plataforma (Game Boy, SNES, Steam, etc.)
            - Variables de seguimiento de estado (is_reading_score, current_mapped_gesture, etc.)
            - Contador de FPS para monitoreo de rendimiento
            - Enfriamiento de navegación para prevenir entrada rápida repetida
            - Seguimiento de ruta del explorador para selección de archivo
            - Estado de máquina de tutorial (4-dirección patrón cruz)
            - Conexiones de señales entre Vista y Presenter
            - Callback de procesamiento de fotogramas del motor de visión
            - Inicialización automática de pantalla de plataformas y tutorial si es primera ejecución
        """
        super().__init__()
        self.view = view
        self.model = model
        self.vision = vision_engine
        
        # Mando virtual Xbox 360 - emula un controlador real para compatibilidad con juegos clásicos
        self.gamepad = vg.VX360Gamepad()
        
        # Mapeo de códigos de botones desde nombres de gestos (XUSB_GAMEPAD_*) a constantes de vgamepad
        # Ejemplo: "XUSB_GAMEPAD_B" -> vg.XUSB_BUTTON.XUSB_GAMEPAD_B
        # Casos especiales: L2/R2 son disparadores (strings como "TRIGGER_L") requiriendo valores float
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
        
        # === Variables de Seguimiento de Estado ===
        self.is_reading_score = False  # Bandera: monitoreando puntuación de gesto para mapeo de control
        self.current_mapped_gesture = None  # Gesto actual siendo configurado (ej: "smile", "blink")
        self.last_ui_update_time = 0  # Timestamp de última actualización UI (limita frecuencia de refresco)

        self.app_start_time = time.perf_counter()  # Momento de inicio de aplicación - usado para retraso de precalentamiento
        
        # === Monitoreo de FPS ===
        self.fps_counter = 0  # Contador de fotogramas para cálculo de FPS
        self.last_fps_time = time.perf_counter()  # Última vez que se calculó FPS (intervalos de 1-segundo)
        
        # === Control de Navegación ===
        self.last_nav_time = 0.0  # Timestamp de última navegación UI (ARRIBA/ABAJO/IZQUIERDA/DERECHA)
        self.nav_cooldown = 0.4  # Segundos mínimos entre saltos de navegación (previene navegación repetida rápida)
        
        # === Control de Vídeo ===
        self.is_video_playing = False  # Bandera: si el procesamiento de vídeo está activo (puede pausarse por usuario) 
        self.ignore_gestures_temporary = False  # Bandera para ignorar inputs del usuario brevemente
        
        # Conectar señales y iniciar el motor de visión
        self._connect_view_signals()
        
        # Conectar señal del motor de visión al método de procesamiento de fotogramas del presenter
        # Este es el bucle de eventos principal: el motor de visión emite fotogramas procesados continuamente
        self.vision.frame_processed.connect(self._on_frame_processed)
        
        # Iniciar el hilo de procesamiento de visión
        self.start_video()

        # === Variables del Explorador de Archivos ===
        self.current_explorer_path = os.path.expanduser('~')  # Directorio actual (comienza en carpeta de usuario)
        self.explorer_mode = "FOLDER"  # Modo: "FOLDER" (añadir carpetas ROM) o "EMULATOR" (elegir .exe)
        self.current_setup_console = None  # Qué emulador de consola se está configurando
        self.explorer_page_return_index = 8  # Índice de página a donde volver después de cerrar explorador

        # === Variables de Plataforma/Juegos ===
        self.current_platform = None  # Plataforma seleccionada actualmente (ej: "SNES", "Steam")
        self.handle_selected_navigation_mode(self.model.input_structure.get("noseLeft", {}).get("d-pad", False))

        # === Variables de Tutorial ===
        self.tutorial_sequence = ["RIGHT", "DOWN", "LEFT", "UP"]  # Orden de botones de cruz a presionar
        self.current_tutorial_step = 0  # Progreso a través del tutorial (0-3)
        self.first_time_mapping = False  # Bandera: si es la primera vez que el usuario mapea controles (para mostrar tutorial)

        # === Inicialización de Primera Ejecución ===
        if self.model.is_first_run_session:
            # --- TELEMETRÍA: Iniciar cronómetro del tutorial ---
            self.tutorial_start_time = time.time()
            # 1. Ocultar botones de navegación durante tutorial
            self.view.set_onboarding_mode(True)
            
            # 2. Navegar a página de tutorial
            self.view.show_page(self.view.ui.stackedWidget.indexOf(self.view.ui.tutorialPage))
            
            # 3. Resaltar primer botón (DERECHA)
            self.view.setup_tutorial_step(self.tutorial_sequence[self.current_tutorial_step])
            self.view.ui.label_tut_info.setText("Centra tu cabeza en la cámara\nMueve tu cabeza hacia el botón\nazul y SONRÍE para pulsarlo.")

            # 4. Mostrar diálogo de bienvenida con retraso de 500ms para permitir que UI se renderice primero
            QTimer.singleShot(500, lambda: self.view.show_tutorial_message(
                "¡Bienvenido!", 
                "Parece que es la primera vez que usas la aplicación.\n\nVamos a configurar tus controles para que puedas manejar el ordenador con la cara.\n\nSONRÍE para CONTINUAR."
            ))


    def _connect_view_signals(self):
        """
        Establecer conexiones de señal-slot entre Vista y Presenter.
        
        Vincula todas las señales de la Vista (interacciones de usuario) a métodos controladores del Presenter.
        Implementa la arquitectura dirigida por señales donde la Vista no modifica directamente el Modelo;
        en su lugar, emite señales que el Presenter interpreta y actúa sobre.
        
        Señales conectadas incluyen:
        - Vídeo: pip_toggled, video_control_toggled, stop_reading_score
        - Navegación: navigation_requested (cambios de página)
        - Gestos: gesture_selected (mapeo de control)
        - Perfiles: load_profiles_requested, profile_accepted, save_as_requested
        - Juegos: games_catalog_requested, scan_games_requested, game_launch_requested
        - Explorador: explorer_opened, explorer_folder_clicked, explorer_up_clicked, etc.
        - Emuladores: emulator_settings_opened, emulator_setup_requested, emulator_exe_chosen
        - Plataformas: platform_selected, remove_platform
        - Controles: controls_opened, controls_closed
        - Configuración de Navegación: navigation_settings_opened, save_navigation_requested, selectedNavigationMode
        - Tutorial: tutorial_step_clicked
        """
        # Señales de control de vídeo
        self.view.pip_toggled.connect(self.view.toggle_pip)
        self.view.video_control_toggled.connect(self.toggle_video)
        self.view.navigation_requested.connect(self.view.show_page)
        
        # Señales de mapeo de control de gestos
        self.view.gesture_selected.connect(self.handle_gesture_selection)
        self.view.stop_reading_score.connect(self.stop_reading)

        # Señales de gestión de perfiles
        self.view.save_controls.connect(self.save_control_mapping)
        self.view.save_mapping_current.connect(self.save_control_mapping_current)
        self.view.load_profiles_requested.connect(self.handle_load_profiles_requested)
        self.view.profile_accepted.connect(self.handle_profile_accepted)
        self.view.save_as_requested.connect(self.handle_save_as_requested)

        # Señales del catálogo de juegos
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
        self.view.open_save_as_requested.connect(self.handle_open_save_as)

        self.view.tutorial_step_clicked.connect(self.handle_tutorial_click)
        
        # Preparar pantalla de plataformas al iniciar
        self.handle_platforms_screen_requested()

        # --- TELEMETRÍA: Conectar la nueva señal de la vista ---
        self.view.mapping_canceled.connect(self.handle_mapping_canceled)

        self.view.application_restored.connect(self.handle_application_restored)
        

    # ===========================
    # MÉTODOS DE CONTROL DE VÍDEO
    # ===========================

    def start_video(self):
        """
        Iniciar procesamiento de vídeo desde la cámara.
        
        Establece la bandera is_video_playing y lanza el hilo del motor de visión.
        Actualiza el texto del botón a "Parar Vídeo".
        """
        self.is_video_playing = True
        
        # Iniciar el hilo de la cámara si no está corriendo
        if not self.vision.isRunning():
            self.vision.start()
            
        self.view.ui.stopButton.setText("Parar Vídeo")

    def stop_video(self):
        """
        Pausar procesamiento de vídeo (fotogramas se ignoran).
        
        Establece is_video_playing a False, haciendo que _on_frame_processed salte procesamiento.
        Actualiza el texto del botón a "Reanudar Vídeo".
        Nota: No detiene el hilo del motor de visión; solo ignora su salida.
        """
        self.is_video_playing = False
        self.view.ui.stopButton.setText("Reanudar Vídeo")

    def toggle_video(self):
        """
        Alternar procesamiento de vídeo encendido o apagado.
        
        Llama a start_video() o stop_video() dependiendo del estado actual.
        """
        if self.is_video_playing:
            self.stop_video()
        else:
            self.start_video()

    def stop_reading(self):
        """
        Detener monitoreo de puntuación de gesto durante mapeo de control.
        
        Establece is_reading_score a False, previniendo actualizaciones de barra de puntuación en _on_frame_processed.
        """
        self.is_reading_score = False

    def save_control_mapping_current(self):
        """
        Guardar mapeo de control actual y volver al catálogo de gestos.
        
        Llama a model.save_inputs() para persistir configuración en memoria a JSON.
        """
        self.model.save_inputs()  # Guardar configuración JSON
        self.model.log_telemetry("save_load_actions_count") # <-- TELEMETRÍA
        self.view.set_save_button_state(False)

    def handle_gesture_selection(self, gesture_button):
        """
        Manejar usuario haciendo clic en botón de gesto (Sonrisa, Parpadeo, etc.).
        """
        gesture_name = gesture_button.text()
        gesture_code = gesture_button.property("gesture")
        self.current_mapped_gesture = gesture_code
        self.view.set_mapping_label(gesture_code, gesture_name)
        self.is_reading_score = True
        
        # --- CORRECCIÓN: Limpiar cualquier botón (naranja) o categoría iluminada del gesto anterior ---
        self.view.clear_selection()
        
        # 1. Resaltar la categoría de gesto en la UI
        gesture_type = self.model.get_type_from_gesture(gesture_code)
        self.view.highlight_category(gesture_type)
        
        # 2. Hacer clic automático en botón de entrada si ya está mapeado
        gesture_input = self.model.get_input_from_gesture(gesture_code)
        if gesture_input:
            self.view.click_input_button(gesture_input)
            
        # 3. Sincronizar slider con umbral actual en modelo
        gesture_data = self.model.input_structure.get(gesture_code, {})
        current_threshold = int(gesture_data.get("threshold", 0.5) * 100)
        self.view.set_slider_threshold(current_threshold)
        
        self.model.log_telemetry("enter_actions_count") # <-- TELEMETRÍA   
        self.view.show_page(2)  # Navegar a página de mapeo de control
        if self.first_time_mapping:
            self.first_time_mapping = False
            self.view.show_tutorial_message(
                "Asignación y Calibración", 
                f"Ahora vamos a configurar {gesture_name}.\n\nElige \"Botón del Mando\" para asignar un botón del mando de consola\nElige \"Acción del Sistema\" para asignar acciones como hacer Click o cambiar el modo de movimiento.\n\nLa parte de abajo te permite calibrar el gesto.\nPulsa el botón \"-\" para que sea más fácil de detectar y \"+\" para hacerlo más difícil.\n\nCuando hayas terminado, pulsa el botón de 'Guardar y Volver'."
            )

    def handle_mapping_canceled(self):
        """El usuario abortó la configuración saliendo con el botón Volver."""
        self.model.log_telemetry("back_from_actions_count") # <-- TELEMETRÍA

    # ===========================
    # BUCLE PRINCIPAL - PROCESAMIENTO DE FOTOGRAMAS
    # ===========================

    def _on_frame_processed(self, frame, blendshapes, landmarks, is_new_processing):
        """
        Callback principal del bucle de procesamiento - ejecutado por cada fotograma procesado por el motor de visión.
        
        Esta es la función más crítica de rendimiento. Se ejecuta en el hilo de visión a ~30 FPS.
        
        Estructura de la función:
        BLOQUE 1: Lógica CORE (limitada por TARGET_FPS del motor de visión)
          - Actualizar puntuaciones de gestos cada ~33ms (30 FPS)
          - Procesar lógica de mando virtual
          - Calcular FPS para monitoreo
        
        BLOQUE 2: Lógica de UI (velocidad máxima, pero con throttle de 50-100ms)
          - Actualizar sliders de navegación en página de calibración
          - Actualizar icono de tutorial en página de tutorial
          - Actualizar barra de puntuación durante mapeo de control
        
        BLOQUE 3: Preparación de datos HUD (Visor Frontal)
          - Determinar qué botones del mando están activos
          - Calcular dirección de movimiento de la cabeza
        
        BLOQUE 4: Actualizar Vista
          - Renderizar fotograma de vídeo con overlay HUD
          - Mostrar botones activos e indicadores de movimiento
        
        Args:
            frame: numpy.ndarray - fotograma RGB de la cámara (H x W x 3)
            blendshapes: dict - puntuaciones de BlendShapes MediaPipe (ej: {"smile": 0.85, ...})
            landmarks: list - landmarks faciales 468 puntos de MediaPipe
            is_new_processing: bool - True si es un nuevo fotograma procesado, False si es frame interpolado
        """
        # Si el vídeo está pausado desde la UI, ignorar el fotograma
        if not self.is_video_playing:
            return

        # ==========================================
        # BLOQUE 1: LÓGICA CORE (Limitada por TARGET_FPS)
        # ==========================================
        # Esta sección se ejecuta cuando hay un nuevo fotograma procesado por MediaPipe (cada ~33ms a 30 FPS)
        if is_new_processing:
            # Esperar 4 segundos para que la cámara se caliente y se calibre
            if (time.perf_counter() - self.app_start_time) >= 4.0:
                # Actualizar puntuaciones de gestos en el modelo
                self.model.update_gesture_scores(blendshapes)
                
                # --- Ignorar comandos si estamos en enfriamiento (cooldown) ---
                if not self.view.ignore_gestures and not getattr(self, 'ignore_gestures_temporary', False):
                    # Procesar lógica de mando virtual (evaluar umbrales, emitir botones)
                    self._process_gamepad_logic(landmarks)

            # Contar fotograma para cálculo de FPS
            self.fps_counter += 1
            current_time = time.perf_counter()
            
            # Actualizar display de FPS cada segundo
            if (current_time - self.last_fps_time) >= 1.0:
                real_fps = int(self.fps_counter / (current_time - self.last_fps_time))
                self.view.update_fps(real_fps)
                self.fps_counter = 0
                self.last_fps_time = current_time

        # ==========================================
        # BLOQUE 2: LÓGICA DE UI (Velocidad máxima)
        # ==========================================
        # Esta sección se ejecuta para cada fotograma (incluso interpolados) pero se limita su frecuencia por página
        current_time = time.perf_counter()

        # --- Actualización de sliders de navegación en página de calibración ---
        if self.view.ui.stackedWidget.currentWidget().objectName() == "navigationPage":
            # Limitar actualizaciones a 20 FPS (50ms) para evitar sobrecarga
            if (current_time - self.last_ui_update_time) >= 0.05: 
                if landmarks:
                    nose = landmarks[1]
                    # Al hacer (1.0 - valor), invertimos la dirección de la barra azul.
                    # Ahora, al mover la cabeza arriba o a la izquierda, la barra irá a la derecha.
                    ui_x = int((1.0 - nose.x) * 100)
                    ui_y = int((1.0 - nose.y) * 100)
                    # Invertir valores: mover cabeza arriba/izquierda = barra va derecha (intuitivo para calibración)
                    self.view.update_navigation_sliders(ui_x, ui_y)
                self.last_ui_update_time = current_time

        elif self.view.ui.stackedWidget.currentWidget().objectName() == "tutorialPage":
            # Actualizar icono de tutorial basado en foco del widget (indicar si botón correcto tiene foco)
            if (current_time - self.last_ui_update_time) >= 0.1:
                # Verificar de forma segura si tutorial sigue activo
                if hasattr(self, 'tutorial_sequence') and self.current_tutorial_step < len(self.tutorial_sequence):
                    target = self.tutorial_sequence[self.current_tutorial_step]
                    self.view.update_tutorial_icon(target)
                self.last_ui_update_time = current_time

        elif self.is_reading_score and self.current_mapped_gesture:
            # Actualizar barra de puntuación de gesto durante mapeo de control (mostrar si umbral alcanzado)
            if (current_time - self.last_ui_update_time) >= 0.1:
                score = self.model.get_score(self.current_mapped_gesture)
                score_int = int(score * 100)
                threshold = self.view.get_slider_threshold()
                # Mostrar barra de progreso y cambiar color si supera umbral
                self.view.update_score_bar(score_int, score_int >= threshold)
                self.last_ui_update_time = current_time

        # Convertir fotograma OpenCV a QPixmap para renderización Qt
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_frame.shape
        qt_img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # ==========================================
        # BLOQUE 3: PREPARACIÓN DE DATOS HUD
        # ==========================================
        # Compilar estado de botones activos y dirección de movimiento para renderización overlay
        target_buttons = self.platform_buttons.get(self.current_platform, [])
        
        # 1. Inicializar todos los botones de plataforma como inactivos (False) por defecto
        input_states = {btn: False for btn in target_buttons}

        # 2. Iterar a través de gestos para ver si algún botón mapeado está activo actualmente
        for gesture_name, gesture_data in self.model.input_structure.items():
            btn_code = gesture_data.get("input")
            # Si el botón mapeado pertenece a la plataforma actual
            if btn_code in input_states:
                # Usar 'or' para que si múltiples gestos mapean al mismo botón,
                # permanezca True si al menos uno está activo
                input_states[btn_code] = input_states[btn_code] or gesture_data.get("active", False)

        # Obtener dirección de movimiento basada en seguimiento de nariz
        movement_direction = self._calculate_movement_direction()

        # ==========================================
        # BLOQUE 4: ACTUALIZAR VISTA
        # ==========================================
        # Renderizar fotograma con overlay HUD mostrando botones activos e indicadores de movimiento
        self.view.update_main_video(pixmap, input_states, movement_direction, self.current_platform, self.using_dPad)

    def _process_gamepad_logic(self, landmarks):
        """
        Evaluar umbrales de gestos, disparar eventos de mando virtual, y mover joysticks analógicos.
        
        Esta función implementa la lógica central de mapeo de gestos a entrada de mando.
        Se ejecuta una vez por fotograma procesado (no interpolado).
        
        Realiza dos operaciones principales:
        1. GESTOS DE BOTONES: Evaluar cada gesto contra su umbral y emitir eventos de botón
        2. GESTOS DE JOYSTICK: Posición de nariz controla joystick analógico izquierdo
        
        Args:
            landmarks: list - 468 landmarks faciales de MediaPipe (la nariz en el índice 1)
        """
        inputs = self.model.input_structure

        # === PARTE 1: EVALUAR GESTOS DE BOTONES Y MODOS ===
        # Iterar a través de todos los gestos excepto los gestos de nariz (que se manejan por separado)
        for gesture_name, data in inputs.items():
            # Saltamos los gestos de la nariz en este bucle, se evalúan en PARTE 2
            if gesture_name.startswith("nose"):
                continue

            score = data.get("score", 0.0)  # Puntuación actual del gesto (0.0 - 1.0)
            threshold = data.get("threshold", 0.5)  # Umbral de activación (0.0 - 1.0)
            is_currently_active = data.get("active", False)  # Estado anterior del gesto
            
            # Qué debe hacer este gesto (pushInputButton o changeMovementMode)
            funcion_asignada = data.get("function")
            action_code = data.get("input")

            # Lógica de detección de cambio de estado (transición)
            if score >= threshold:
                if not is_currently_active:
                    # EL USUARIO ACABA DE SUPERAR EL UMBRAL - transición INACTIVO -> ACTIVO
                    # Ejecutar acción de presión (emitir botón del mando o cambiar modo)
                    self._execute_press_action(data)
                    self.model.input_structure[gesture_name]["active"] = True
                        
            else:
                if is_currently_active:
                    # EL USUARIO CAYÓ POR DEBAJO DEL UMBRAL - transición ACTIVO -> INACTIVO
                    # Ejecutar acción de liberación (liberar botón del mando)
                    self._execute_release_action(data)
                    self.model.input_structure[gesture_name]["active"] = False

        # === PARTE 2: EVALUAR GESTOS DE JOYSTICK (Movimiento de la nariz) ===
        # La nariz es el punto de control principal para navegación/movimiento
        if landmarks:
            # En MediaPipe, el índice 1 corresponde a la punta de la nariz
            nose = landmarks[1]

            jx, jy = 0, 0  # Valores del joystick analógico (-32767 a +32767)
            
            # Rastrear estado individual de cada dirección para visualización/HUD
            is_left, is_right, is_up, is_down = False, False, False, False

            # Obtener umbrales de nariz configurados (valores entre 0.0 y 1.0)
            # Estos definen qué tan extremo es el movimiento de cabeza antes de activar
            th_left = inputs.get("noseLeft", {}).get("threshold", 0.6)
            th_right = inputs.get("noseRight", {}).get("threshold", 0.4)
            th_up = inputs.get("noseUp", {}).get("threshold", 0.4)
            th_down = inputs.get("noseDown", {}).get("threshold", 0.6)

            # === Evaluar Eje X (IZQUIERDA/DERECHA) ===
            # nose.x va de 0.0 (izquierda) a 1.0 (derecha)
            if nose.x >= th_left:
                # Nariz hacia la izquierda = joystick hacia la izquierda
                jx = -20000
                is_left = True
            elif nose.x <= th_right:
                # Nariz hacia la derecha = joystick hacia la derecha
                jx = 20000
                is_right = True

            # === Evaluar Eje Y (ARRIBA/ABAJO) ===
            # nose.y va de 0.0 (arriba) a 1.0 (abajo)
            if nose.y >= th_down:
                # Nariz hacia abajo = joystick hacia abajo
                jy = -20000
                is_down = True
            elif nose.y <= th_up:
                # Nariz hacia arriba = joystick hacia arriba
                jy = 20000
                is_up = True

            # Control de modo: Continuo (libre movimiento) vs Pasos (movimiento por etapas)
            # En modo de pasos, solo emitir un movimiento por fotograma procesado
            if not self.model.is_continuous_mode and (inputs.get("noseUp", {}).get("active") or inputs.get("noseDown", {}).get("active")):
                jy = 0  # Congelar movimiento vertical en modo pasos
            if not self.model.is_continuous_mode and (inputs.get("noseLeft", {}).get("active") or inputs.get("noseRight", {}).get("active")):
                jx = 0  # Congelar movimiento horizontal en modo pasos

            # === Manejar Eje X en Mando Virtual ===
            if jx == 20000:
                # Navegar a la DERECHA en la interfaz
                self.navigate_interface("RIGHT") 
                # Emitir botón D-Pad si está en modo D-Pad (no analógico)
                if self.using_dPad:
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            
            elif jx == -20000:
                # Navegar a la IZQUIERDA en la interfaz
                self.navigate_interface("LEFT")  
                if self.using_dPad:
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            else:
                # No hay movimiento horizontal - liberar ambos botones D-Pad
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            
            # === Manejar Eje Y en Mando Virtual ===
            if jy == 20000:
                # Navegar ARRIBA en la interfaz
                self.navigate_interface("UP")
                if self.using_dPad:
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            elif jy == -20000:
                # Navegar ABAJO en la interfaz
                self.navigate_interface("DOWN")  
                if self.using_dPad:
                    self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            else:
                # No hay movimiento vertical - liberar ambos botones D-Pad
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)  
                self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)

            # === Sincronizar estado de direcciones con el modelo ===
            # El modelo rastrea esto para visualización HUD y lógica de modo
            if "noseLeft" in inputs: inputs["noseLeft"]["active"] = is_left
            if "noseRight" in inputs: inputs["noseRight"]["active"] = is_right
            if "noseUp" in inputs: inputs["noseUp"]["active"] = is_up
            if "noseDown" in inputs: inputs["noseDown"]["active"] = is_down

            # === Mover Joystick Analógico Izquierdo del Mando Xbox ===
            # Este es el movimiento suave continuo (opuesto al D-Pad discreto)
            self.gamepad.left_joystick(x_value=jx, y_value=jy)

        # === PARTE 3: ENVIAR ACTUALIZACIÓN AL DRIVER DE MANDO VIRTUAL ===
        # Sincronizar todos los cambios de estado con el driver de Windows
        self.gamepad.update()

    def shutdown(self):
        # Ya no hay timer que detener, solo liberamos la cámara y el mando
        self.model.export_telemetry_csv() # <-- TELEMETRÍA: Exportar al disco antes de morir
        self.vision.release_resources()
        self.gamepad.reset()
        self.gamepad.update()

    def save_control_mapping(self, gesture_code, input_code, threshold):
        """Recibe la señal del botón Guardar en la UI, actualiza la memoria y vuelve al menú."""
        # 1. Ejecutamos la actualización en memoria
        self.model.save_control_mapping(gesture_code, input_code, threshold)

        self.view.set_save_button_state(True)
        
        # 2. Detenemos la actualización rápida de la barra de progreso
        self.is_reading_score = False
        self.current_mapped_gesture = None

        self.view.ui.stackedWidgetAcciones.setCurrentIndex(0)
        
        # 3. Ordenamos a la Vista que vuelva a la página 1 (El catálogo de gestos)
        self.view.show_page(1)


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
        self.view.set_save_button_state(False)
        # 2. EXTRAER EL VALOR DEL D-PAD:
        # Asumimos que todos los gestos de nariz tienen el mismo ajuste de D-Pad.
        # Leemos el primer gesto de nariz que encontremos.
        new_dpad_mode = False # Valor por defecto

        new_dpad_mode = self.model.input_structure["noseLeft"].get("d-pad", False)

        # 3. Actualizar el estado interno y avisar a la lógica
        self.handle_selected_navigation_mode(new_dpad_mode)
        
        # 4. OPCIONAL: Actualizar los botones de la UI para que reflejen el modo cargado
        # Esto es vital para que el usuario sepa visualmente qué modo se ha cargado
        
        self.model.log_telemetry("save_load_actions_count") # <-- TELEMETRÍA
        # 5. Volver al catálogo de gestos (Página 1)
        self.view.show_page(1)

    def handle_save_as_requested(self, filename):
        """Guarda la configuración actual en un nuevo archivo."""
        self.model.save_as_profile(filename)
        self.model.log_telemetry("save_load_actions_count") # <-- TELEMETRÍA
        self.view.set_save_button_state(False)
        # Si estábamos en el tutorial, este es el verdadero final
        if self.model.is_first_run_session:
            self.model.complete_onboarding()
            self.view.set_onboarding_mode(False)
            self.view.show_page(self.view.ui.stackedWidget.indexOf(self.view.ui.platformsPage))
            
            # --- NUEVO: Activar bloqueo temporal de 0.5 segundos ---
            self.ignore_gestures_temporary = True
            
            # Usar una función local para liberar el bloqueo
            def reactivar_gestos():
                self.ignore_gestures_temporary = False
                
            # Programar la liberación para dentro de 500ms
            QTimer.singleShot(500, reactivar_gestos)
            
            # --- FIN NUEVO ---
            
            self.view.show_tutorial_message("¡Hecho!", "Perfil guardado. Ahora ya puedes navegar libremente por los menús.")
            duration = time.time() - self.tutorial_start_time
            self.model.set_tutorial_time(duration) # <-- TELEMETRÍA
            
        else:
            # Comportamiento normal si no es la primera ejecución
            self.view.show_page(self.view.ui.stackedWidget.indexOf(self.view.ui.gesturesPage))


    def handle_games_catalog_requested(self):
        """Solicita los juegos al modelo, ordena pintarlos y cambia a la pantalla de catálogo."""
        lista_juegos = self.obtain_current_platfor_games(self.current_platform)
        self.view.populate_games_catalog(lista_juegos, self.current_platform, self.model.emulators_config.get(self.current_platform))
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
            self.view.populate_games_catalog(lista_actualizada, self.current_platform, self.model.emulators_config.get(self.current_platform))

    def handle_game_launch(self, exe_path):
        """Lanza asíncronamente el ejecutable del juego, URI de Steam o ROM con su emulador asignado."""
        if not exe_path:
            print("Advertencia: Este juego no tiene configurada una ruta de ejecución válida.")
            return

        # 1. Ejecutables nativos o accesos directos de Steam
        if exe_path.startswith("steam://") or exe_path.lower().endswith(".exe"):
            try:
                os.startfile(exe_path)
                print(f"Lanzado con éxito: {exe_path}")
                # --- NUEVO: Minimizar ventana tras un lanzamiento exitoso ---
                self.view.launch_pip()
                self.view.showMinimized()
                self.model.change_movement_mode(True)  # Cambiar a modo continuo para jugar
            except Exception as e:
                print(f"Error crítico al intentar abrir el juego en '{exe_path}': {e}")
            return

        # 2. Es una ROM. Buscar su consola y emulador.
        _, extension = os.path.splitext(exe_path)
        console_name = self.model.get_console_from_extension(extension)

        emulator_path = "Default"
        if console_name:
            emulator_path = self.model.emulators_config.get(console_name, "Default")

        try:
            # Si está configurado en Predeterminado, o si el .exe elegido manualmente fue borrado del disco duro
            if emulator_path == "Default" or not os.path.exists(emulator_path):
                if self.has_windows_default_app(exe_path):
                    os.startfile(exe_path)
                    print(f"Lanzando ROM con la aplicación predeterminada de Windows: {exe_path}")
                    
                    # --- NUEVO: Minimizar ventana tras un lanzamiento exitoso ---
                    self.view.launch_pip()
                    self.view.showMinimized()
                    self.model.change_movement_mode(True)  # Cambiar a modo continuo para jugar
                else:
                    print(f"Error: No hay aplicación predeterminada en Windows para abrir la extensión de {exe_path}")
                    self.view.show_tutorial_message(
                    "Error",
                    f"¡No hay aplicación predeterminada en Windows para abrir la extensión de {exe_path}!\n\nPor favor, asigna una aplicación por defecto para este archivo o configura uno pulsando en el botón de \"Emulador\" situado encima."
                    )
            else:
                # Lanzar el emulador personalizado, pasando la ruta de la ROM como argumento principal
                subprocess.Popen([emulator_path, exe_path])
                print(f"Lanzando ROM con emulador personalizado ({console_name}): {emulator_path} -> {exe_path}")
                # --- NUEVO: Minimizar ventana tras un lanzamiento exitoso ---
                self.view.launch_pip()
                self.view.showMinimized()
                self.model.change_movement_mode(True)  # Cambiar a modo continuo para jugar
                
        except Exception as e:
            print(f"Error crítico al lanzar la ROM: {e}")

    def handle_explorer_opened(self):
        self.explorer_mode = "FOLDER"
        rutas_guardadas = self.model.get_rom_folders()
        self.model.log_telemetry("enter_explorer_count") # <-- TELEMETRÍA
        # NUEVO: Validamos proactivamente que la última ruta guardada siga existiendo físicamente
        if rutas_guardadas and os.path.exists(rutas_guardadas[-1]):
            self.current_explorer_path = rutas_guardadas[-1]
        else:
            # Alternativa segura si la lista está vacía o la carpeta fue eliminada
            self.current_explorer_path = os.path.expanduser('~')
            
        self.refresh_explorer()
        self.view.show_page(6)

    def refresh_explorer(self): 
        if self.current_explorer_path == "DRIVES":
            drives = [(f"{d}:\\", "folder") for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            self.view.populate_explorer("Este Equipo (Discos Duros)", drives, mode=self.explorer_mode)
            return

        try:
            items = os.listdir(self.current_explorer_path)
            
            # Obtener siempre las carpetas
            folders = [f for f in items if os.path.isdir(os.path.join(self.current_explorer_path, f))]
            folders.sort(key=str.lower)
            content_list = [(f, "folder") for f in folders]
            
            # Inyectar archivos .exe SOLAMENTE si estamos buscando un emulador
            if self.explorer_mode == "EMULATOR":
                exes = [f for f in items if f.lower().endswith('.exe')]
                exes.sort(key=str.lower)
                content_list.extend([(f, "exe") for f in exes])

            # USAMOS LA MEMORIA DE LA CLASE: self.explorer_page_return_index
            self.view.populate_explorer(self.current_explorer_path, content_list, mode=self.explorer_mode, page_index_return=self.explorer_page_return_index)
            
        # NUEVO: Añadimos FileNotFoundError a la tupla de excepciones para blindar el proceso
        except (PermissionError, FileNotFoundError) as e:
            print(f"Alerta del explorador: No se pudo acceder a {self.current_explorer_path}. Detalles: {e}")
            
            # Si la ruta no existe o está denegada, forzamos un rebote seguro a la raíz del sistema
            self.current_explorer_path = "DRIVES"
            self.refresh_explorer()

    def handle_explorer_select(self):
        """La acción depende del modo actual del explorador."""
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
            # El usuario hizo clic en "PREDETERMINADO DE WINDOWS"
            if self.current_setup_console:
                self.model.emulators_config[self.current_setup_console] = "Default"
                self.model.save_emulators_config()
                
                # Refrescamos la pantalla de ajustes
                self.view.populate_emulator_settings(self.model.emulators_config)
                
                # --- CORRECCIÓN: Refrescar el botón del emulador si volvemos al catálogo ---
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
        """Vuelve a la página correcta dependiendo de desde dónde se lanzó el explorador."""
        self.model.log_telemetry("back_from_explorer_count") # <-- TELEMETRÍA
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
                return  # Omitir si el tiempo de enfriamiento no ha terminado
            
            # Si ha pasado suficiente tiempo, actualizar el temporizador y proceder al salto
            self.last_nav_time = current_time

        # 1. El gesto de "Aceptar" sigue inyectando un Enter normal
        if direction == "ENTER":
            current_widget = QApplication.focusWidget()
            if current_widget:
                # La forma más infalible de activar un botón en Qt
                if hasattr(current_widget, "click"):
                    current_widget.click()
                else:
                    # Alternativa para widgets que no son botones (Qt prefiere Espacio sobre Intro)
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

        # 3. Escanear TODOS los componentes en la interfaz actual
        for candidate in window.findChildren(QWidget):
            if not candidate.isVisible() or not candidate.isEnabled() or candidate == current_widget:
                continue
            
            if candidate.focusPolicy() == Qt.NoFocus:
                continue

            # Límites del candidato (Caja delimitadora en lugar de solo el centro)
            candidate_rect = candidate.rect()
            top_left = candidate.mapToGlobal(candidate_rect.topLeft())
            bottom_right = candidate.mapToGlobal(candidate_rect.bottomRight())
            
            # Los centros todavía se usan para determinar la dirección general (Izquierda/Derecha/Arriba/Abajo)
            center_cand = candidate.mapToGlobal(candidate_rect.center())
            x2, y2 = center_cand.x(), center_cand.y()
            
            dx = x2 - x1
            dy = y2 - y1

            # --- CORRECCIÓN 1: Distancia de la caja delimitadora ---
            # Si x1 está dentro del ancho del candidato, la distancia horizontal es 0
            dist_x = 0
            if x1 < top_left.x(): 
                dist_x = top_left.x() - x1
            elif x1 > bottom_right.x(): 
                dist_x = x1 - bottom_right.x()
            
            # Si y1 está dentro de la altura del candidato, la distancia vertical es 0
            dist_y = 0
            if y1 < top_left.y(): 
                dist_y = top_left.y() - y1
            elif y1 > bottom_right.y(): 
                dist_y = y1 - bottom_right.y()

            is_valid = False
            distance = float('inf')

            # 4. Filtro direccional con penalización
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

            # 5. Guardar si es el candidato más cercano
            if is_valid and distance < min_distance:
                min_distance = distance
                best_candidate = candidate

        # 6. Ejecutar el salto de foco
        if best_candidate:
            best_candidate.setFocus()

            # --- CORRECCIÓN 2: Desplazamiento automático si el botón está dentro de un área de scroll ---
            
            parent = best_candidate.parentWidget()
            
            # Recorrer el árbol de widgets hacia arriba para ver si estamos dentro de un QScrollArea
            while parent:
                if isinstance(parent, QScrollArea):
                    # Asegurar que el widget sea completamente visible, añadiendo un margen de 10px por estética
                    parent.ensureWidgetVisible(best_candidate, 10, 10)
                    break
                parent = parent.parentWidget()

    def _execute_press_action(self, input_data):
        """Actúa como enrutador cuando un gesto supera el umbral."""
        action_code = input_data.get("input")
        if not action_code or action_code == "SYS_NONE":
            return
            
        # 1. Botón de mando virtual / Disparador
        if action_code.startswith("XUSB_"):
            if action_code == "XUSB_GAMEPAD_L2":
                self.gamepad.left_trigger_float(1.0)  # Presión al 100%
            elif action_code == "XUSB_GAMEPAD_R2":
                self.gamepad.right_trigger_float(1.0) # Presión al 100%
            else:
                # Botones normales (A, B, L1, Start...)
                self.gamepad.press_button(button=self.buttons_map[action_code])
            
        # 2. Acción interna del sistema
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
        """Libera la acción cuando el usuario relaja el gesto."""
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
        """Prepara el explorador para elegir un ejecutable para una consola específica."""
        self.current_setup_console = console_name
        self.explorer_mode = "EMULATOR"
        
        # GUARDAMOS EL ÍNDICE EN LA MEMORIA DEL PRESENTER
        self.explorer_page_return_index = page_index_return

        self.current_explorer_path = os.path.expanduser('~')
        self.model.log_telemetry("enter_explorer_count")
        self.refresh_explorer() # Ya no pasamos el parámetro por aquí
        self.view.show_page(6)

    def handle_emulator_exe_chosen(self, filename, page_index_return=None):
        """Se dispara cuando se hace clic en un .exe en el explorador."""
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
        self.view.populate_games_catalog(juegos_filtrados, platform_name, self.model.emulators_config.get(self.current_platform))
        
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
        self.model.log_telemetry("back_from_gestures_count") # <-- TELEMETRÍA
        # 1. Ocultamos la imagen para que no moleste en el resto de la app
        self.view.hide_controller_image()
        self.view.set_save_button_state(False)
        self.model.load_inputs()  # <-- Recargamos los valores del modelo para que la vista vuelva a la normalidad
        # 2. Volvemos al menú principal / catálogo (Sustituye el 0 por el índice que necesites)
        self.view.show_page(0)

    def _calculate_movement_direction(self):
        """Devuelve la dirección activa actual basada en el seguimiento de la nariz."""
        inputs = self.model.input_structure
        
        up = inputs.get("noseUp", {}).get("active", False)
        down = inputs.get("noseDown", {}).get("active", False)
        left = inputs.get("noseLeft", {}).get("active", False)
        right = inputs.get("noseRight", {}).get("active", False)
        
        # Movimientos diagonales
        if up and right: return "NE"
        if up and left: return "NW"
        if down and right: return "SE"
        if down and left: return "SW"
        
        # Movimientos cardinales
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


    def handle_open_save_as(self):
        """Genera un nombre de archivo por defecto y abre el teclado virtual."""
        import datetime
        
        # Añadimos %H (Hora en 24h) y %M (Minutos). Ej: 08-06-2026_12-21
        fecha_hora = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
        
        if self.current_platform:
            # Quitamos los espacios de la plataforma (ej: 'Game Boy' -> 'GameBoy')
            plataforma_limpia = self.current_platform.replace(" ", "")
            nombre_defecto = f"{plataforma_limpia}_{fecha_hora}"
        else:
            nombre_defecto = f"Perfil_{fecha_hora}"
            
        # Ordenamos a la vista que abra el teclado con el texto inyectado
        self.view.open_virtual_keyboard(nombre_defecto)

    def handle_tutorial_click(self, direction):
        """Avanza al siguiente paso del tutorial si el usuario pulsa el botón correcto."""
        if direction == self.tutorial_sequence[self.current_tutorial_step]:
            self.current_tutorial_step += 1
            
            if self.current_tutorial_step < len(self.tutorial_sequence):
                siguiente_direccion = self.tutorial_sequence[self.current_tutorial_step]
                self.view.setup_tutorial_step(siguiente_direccion)
                mensajes = [
                    "¡Genial!\n\nAhora ve hacia ABAJO.",
                    "¡Perfecto!\n\nAhora a la IZQUIERDA.",
                    "¡Casi está!\n\nPor último, hacia ARRIBA."
                ]
                self.view.ui.label_tut_info.setText(mensajes[self.current_tutorial_step - 1])
                
            else:
                # FINAL DE LA CRUZ: Ha superado la prueba de movimiento.
                # Le mandamos a la página de gestos para que cree su perfil obligatoriamente.
                self.view.ui.label_tut_info.setText("¡Prueba superada!\n\nCargando configuración...")
                self.handle_controls_opened()
                # Mostrar diálogo de gestos con retraso de 300ms para permitir que UI se renderice primero
                QTimer.singleShot(300, lambda: self.view.show_tutorial_message(
                    "Configuración de Controles",
                    "¡Has completado el primer paso!\n\nVamos a configurar tus controles para que puedas manejar el ordenador con la cara.\n\nMuevete hacia el botón con el gesto que quieras configurar y SONRIE para continuar.\n\nCuando hayas terminado, pulsa el botón de 'Guardar Como'."
                ))
                self.first_time_mapping=True


    def handle_application_restored(self):
        """Se ejecuta cuando la ventana vuelve a primer plano. Cambia el modo de movimiento."""
        self.model.change_movement_mode(False)  # Cambiar a modo discreto (pasos) cuando la aplicación se restaura a primer plano


    def has_windows_default_app(self, filepath):
        """
        Consulta a la API de Windows si existe un programa predeterminado 
        asociado a la extensión de este archivo.
        """
        if not os.path.exists(filepath):
            return False
            
        # Buffer para almacenar la ruta del ejecutable asociado si se encuentra
        executable = ctypes.create_unicode_buffer(1024)
        
        # Llamada a la API nativa de Windows
        result = ctypes.windll.shell32.FindExecutableW(filepath, None, executable)
        
        # FindExecutableW devuelve un valor > 32 si encuentra una asociación válida.
        # Valores <= 32 indican errores (archivo no encontrado, sin asociación, etc.)
        return result > 32
        
