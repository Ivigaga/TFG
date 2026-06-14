"""=============================================================================
MÓDULO view.py - INTERFAZ GRÁFICA DE USUARIO (GUI)
=============================================================================
Responsable de toda la presentación visual y interacción del usuario.
Implementa el patrón MVP (Model-View-Presenter).

Componentes principales:
  - PipWindow: Ventana flotante para video Picture-in-Picture
  - MainView: Ventana principal con todos los controles y pantallas

Características:
  - Teclado virtual personalizado
  - Explorador de archivos interactivo
  - Configuración dinámica de emuladores
  - Catálogo de juegos y plataformas
  - Sistema de perfiles de control
  - Tutorial interactivo integrado
=============================================================================
"""

import os

from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QButtonGroup, QToolButton, QSizePolicy
from PySide6.QtGui import QColor, QFont, QIcon, QImage, QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtCore import QEvent, QPoint, Signal, Qt, QSize

from model import get_asset_path
from prueba_ui import Ui_MainWindow
import textwrap

class PipWindow(QWidget):
    """
    Ventana flotante (Picture-in-Picture) para mostrar el video de cámara.
    Se mantiene siempre visible sobre otras ventanas y permite al usuario
    ver el feed de video mientras configura otros ajustes.
    """
    # Señal emitida cuando el usuario cierra la ventana con la 'X'
    window_closed = Signal()

    def __init__(self):
        """Inicializa la ventana flotante con tamaño fijo y estilo al-frente."""
        super().__init__()
        self.setWindowTitle("Video PiP")
        self.resize(400, 300)
        # Qt.Tool: hace que sea una ventana flotante independiente
        # Qt.WindowStaysOnTopHint: siempre visible sobre otras ventanas
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.move(0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Etiqueta donde se dibujará el video en tiempo real
        self.video_label = QLabel(self)
        self.video_label.setMinimumSize(100, 100)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black;")
        layout.addWidget(self.video_label)

    def update_image(self, pixmap):
        """Actualiza la imagen mostrada en la ventana PiP.
        
        Args:
            pixmap: QPixmap con el frame del video actual
        """
        self.video_label.setPixmap(pixmap.scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

    def closeEvent(self, event):
        """Captura el evento de cierre de la ventana por parte del usuario.
        
        Emite la señal window_closed para que el presentador pueda actualizar
        el estado de la interfaz principal.
        """
        self.window_closed.emit()  # Notificar al presentador del cierre
        super().closeEvent(event)  # Permitir que Qt complete el cierre


class MainView(QMainWindow):
    """
    Ventana principal de la aplicación.
    
    Responsabilidades:
    - Mostrar la interfaz gráfica del usuario
    - Capturar eventos del usuario (clicks, input)
    - Emitir señales para que el Presentador reaccione
    - Actualizar elementos visuales basado en datos del Modelo
    
    El flujo es: Usuario actúa -> View emite Signal -> Presenter reacciona
    """
    
    # ==================== SEÑALES DE CONTROL DE VIDEO ====================
    pip_toggled = Signal()  # PiP activado/desactivado
    video_control_toggled = Signal()  # Parar/reanudar video
    
    # ==================== SEÑALES DE NAVEGACIÓN ====================
    navigation_requested = Signal(int)  # Cambiar de pantalla (índice de página)
    
    # ==================== SEÑALES DE CONFIGURACIÓN DE GESTOS ====================
    gesture_selected = Signal(object)  # Gesto seleccionado por el usuario
    stop_reading_score = Signal()  # Detener lectura de confianza del gesto
    save_controls = Signal(str, str, int)  # gesture_code, input_code, threshold
    save_mapping_current = Signal()  # Guardar en perfil actual
    
    # ==================== SEÑALES DE PERFILES ====================
    load_profiles_requested = Signal()  # Cargar lista de perfiles
    profile_accepted = Signal(str)  # Aceptar perfil (envía nombre)
    save_as_requested = Signal(str)  # Guardar como nuevo perfil
    open_save_as_requested = Signal()  # Abrir diálogo de guardado

    # ==================== SEÑALES DE JUEGOS ====================
    games_catalog_requested = Signal()  # Solicitar catálogo de juegos
    scan_games_requested = Signal()  # Escanear juegos en carpetas/Steam
    game_launch_requested = Signal(str)  # Lanzar juego (envía ruta ejecutable)

    # ==================== SEÑALES DEL EXPLORADOR DE ARCHIVOS ====================
    explorer_opened = Signal()  # Abrir explorador
    explorer_folder_clicked = Signal(str)  # Entrar en carpeta
    explorer_up_clicked = Signal()  # Subir nivel de directorio
    explorer_select_clicked = Signal()  # Confirmar selección
    explorer_cancel_clicked = Signal()  # Cancelar explorador

    # ==================== SEÑALES DE EMULADORES ====================
    emulator_settings_opened = Signal()  # Abrir configuración de emuladores
    emulator_setup_requested = Signal(str, int)  # (console_name, page_return_index)
    emulator_exe_chosen = Signal(str, int)  # (exe_filename, page_return_index)

    # ==================== SEÑALES DE PLATAFORMAS ====================
    platform_selected = Signal(str)  # Plataforma seleccionada (envía nombre)
    remove_platform = Signal()  # Volver a mostrar todas las plataformas

    # ==================== SEÑALES DE PANTALLA DE CONTROLES ====================
    controls_opened = Signal()  # Abrir pantalla de configuración de gestos
    controls_closed = Signal()  # Cerrar pantalla de configuración

    # ==================== SEÑALES DE NAVEGACIÓN POR CÁMARA ====================
    navigation_settings_opened = Signal()  # Abrir pantalla de calibración
    save_navigation_requested = Signal(int, int, int, int)  # low_x, high_x, low_y, high_y
    selectedNavigationMode = Signal(bool)  # False=Joystick, True=D-Pad
    
    # ==================== SEÑALES DE TUTORIAL ====================
    tutorial_step_clicked = Signal(str)  # Paso del tutorial presionado (UP, DOWN, LEFT, RIGHT)

    def __init__(self):
        """Inicializa la ventana principal y configura todos los componentes."""
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(get_asset_path("images/icon.ico")))
        self.setWindowTitle("FaceDrive")
        self.resize(1020, 751)

        self.ui.stackedWidget.setCurrentIndex(0)
        
        # --- TÉCNICA: "EL TRUCO DEL FANTASMA" PARA OCULTAR LA IMAGEN DEL MANDO ---
        # Sin romper el layout cuando se oculta. Explicación:
        # 1. Capturamos las reglas de tamaño (SizePolicy) del widget
        policy = self.ui.controllerImage.sizePolicy()
        # Inicializar cache de imágenes HUD (se llena dinámicamente durante video)
        self.hud_image_cache = {}
        
        # 2. Indicarle a Qt que RESERVE el espacio físico aunque la imagen esté oculta
        #    Sin esto, cuando ocultamos la imagen, el video se expande y rompe el layout
        policy.setRetainSizeWhenHidden(True)
        self.ui.controllerImage.setSizePolicy(policy)
        
        # 3. Ahora podemos ocultar la imagen de forma segura. El video NO se moverá.
        self.ui.controllerImage.hide()
        self.current_controller_path = ""  # Controlar qué imagen está cargada
        
        # 4. Desactivar el escalado automático del label de video (lo haremos manualmente)
        self.ui.videoLabel.setScaledContents(False)

        # Variable para controlar la ventana PiP
        self.pip_window = None
        
        # Conectar todas las señales de UI con los métodos correspondientes
        self._connect_signals()
        
        # Establecer icono del botón de navegación (nariz)
        self.ui.noseButton.setIcon(QIcon(get_asset_path("images/gestures/movement.png")))
        

    def _connect_signals(self):
        """
        Conecta todos los eventos de la interfaz de usuario con las señales personalizadas.
        Esto permite que el Presentador reaccione a las acciones del usuario.
        """
        
        # ==========================================
        # 1. CONTROLES DE VÍDEO Y PiP
        # ==========================================
        # Botón para extraer/unir la ventana de video flotante
        self.ui.pipButton.clicked.connect(self.pip_toggled.emit)
        # Botón para pausar/reanudar el video
        self.ui.stopButton.clicked.connect(self.video_control_toggled.emit)

        # "F5" pausará/reanudará el vídeo sin importar en qué menú estés
        self.atajo_video = QShortcut(QKeySequence("F5"), self)
        self.atajo_video.activated.connect(self.video_control_toggled.emit)

        # ==========================================
        # 2. ACCESOS A PANTALLAS PRINCIPALES Y MENÚS
        # ==========================================
        # Botones que abren la configuración de controles
        self.ui.controlsButton.clicked.connect(self.controls_opened.emit)
        self.ui.gamesControlsButton.clicked.connect(self.controls_opened.emit)
        # Volver desde la pantalla de gestos
        self.ui.gesturesBackButton.clicked.connect(self.controls_closed.emit)
        
        # Accesos a configuración de emuladores
        self.ui.emulatorsButton.clicked.connect(self.emulator_settings_opened.emit)
        self.ui.pushButton.clicked.connect(self.emulator_settings_opened.emit) # (Considera renombrar 'pushButton' en QtDesigner a algo más descriptivo)
        
        # Volver desde los menús de ajustes
        self.ui.settingsBackButton.clicked.connect(lambda: self.navigation_requested.emit(0))
        self.ui.emulatorSettingsBackButton.clicked.connect(lambda: self.navigation_requested.emit(0))

        # ==========================================
        # 3. CONFIGURACIÓN DE GESTOS Y MAPEO
        # ==========================================
        # Catálogo central de gestos
        for btn in self.ui.gestureButtons.buttons():
            btn.clicked.connect(lambda checked=False, b=btn: self.gesture_selected.emit(b))
            
        # Navegación anidada (Sub-pestañas de Categorías: Mando, Sistema...)
        self.ui.btn_cat_mando.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(1))
        self.ui.btn_cat_sys.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(2))
        self.ui.btn_volver_cat1.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))
        self.ui.btn_volver_cat2.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))

        # Iluminar categoría dinámicamente al seleccionar opciones
        self.ui.controlButtons.buttonClicked.connect(self._on_action_button_clicked)

        # Controles dinámicos del Slider de Umbral (Sensibilidad)
        self.ui.scoreSlider.valueChanged.connect(self._on_slider_value_changed)
        self.ui.btn_plus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() + 5))
        self.ui.btn_minus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() - 5))

        # Botón Guardar Mapeo
        self.ui.controlsSaveButon.clicked.connect(lambda: self.save_controls.emit(self.get_selected_gesture(), self.get_selected_control(), self.get_slider_threshold()))
        self.ui.controlsSaveButon.clicked.connect(self.stop_reading_score.emit)

        # Botón Limpiar/Deseleccionar Mapeo
        self.ui.controlsCleanButton.clicked.connect(self.clear_selection)

        # Botón Cancelar Mapeo (Restaura vistas y detiene lectura)
        self.ui.controlsCancelButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))
        self.ui.controlsCancelButton.clicked.connect(self.stop_reading_score.emit)

        # ==========================================
        # 4. GESTIÓN DE PERFILES (Cargar/Guardar)
        # ==========================================
        # Guardado rápido (en el perfil actual)
        self.ui.gesturesSaveLocalButton.clicked.connect(self.save_mapping_current.emit) 
        
        # Guardar como... (Abre el teclado virtual)
        self.ui.gesturesSaveExternalButton.clicked.connect(self.open_save_as_requested.emit)
        
        # Menú Cargar Perfil
        self.ui.gesturesLoadButton.clicked.connect(self.load_profiles_requested.emit)
        self.ui.loadBackButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.loadAcceptButton.clicked.connect(self._on_accept_profile)
        
        # Grupo exclusivo para los perfiles disponibles (Radio Buttons lógicos)
        self.profile_button_group = QButtonGroup(self)
        self.profile_button_group.setExclusive(True)

        # Teclado Virtual para nombrar perfiles
        self.ui.keyboardCancelButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.keyboardBackspaceButton.clicked.connect(self._on_keyboard_backspace)
        self.ui.keyboardAcceptButton.clicked.connect(self._on_keyboard_accept)
        self.build_virtual_keyboard()

        # ==========================================
        # 5. CATÁLOGO DE JUEGOS
        # ==========================================
        self.ui.gamesBackButton.clicked.connect(self.remove_platform.emit)
        self.ui.gamesScanButton.clicked.connect(self.scan_games_requested.emit)
        self.ui.steamGamesScanButton.clicked.connect(self.scan_games_requested.emit)

        # ==========================================
        # 6. EXPLORADOR DE ARCHIVOS Y CARPETAS
        # ==========================================
        # Botones que abren el explorador desde diferentes pantallas
        self.ui.scanFolderButton.clicked.connect(self.explorer_opened.emit)
        self.ui.gamesScanFolderButton.clicked.connect(self.explorer_opened.emit)
        
        # Navegación interna del explorador
        self.ui.explorerUpButton.clicked.connect(self.explorer_up_clicked.emit)
        self.ui.explorerSelectButton.clicked.connect(self.explorer_select_clicked.emit)
        self.ui.explorerCancelButton.clicked.connect(self.explorer_cancel_clicked.emit) 

        # ==========================================
        # 7. CONFIGURACIÓN DE NAVEGACIÓN (CÁMARA / NARIZ)
        # ==========================================
        # Abrir pantalla de navegación de la nariz
        self.ui.noseButton.clicked.connect(lambda: self.navigation_requested.emit(9))
        self.ui.noseButton.clicked.connect(self.navigation_settings_opened.emit)
        
        # Modos de Navegación (Joystick vs D-Pad)
        self.ui.btn_nav_joystick.clicked.connect(lambda: self.selectedNavigationMode.emit(False))
        self.ui.btn_nav_dpad.clicked.connect(lambda: self.selectedNavigationMode.emit(True))

        if hasattr(self.ui, 'btn_nav_back'):
            self.ui.btn_nav_back.clicked.connect(lambda: self.navigation_requested.emit(
                self.ui.stackedWidget.indexOf(self.ui.gesturesPage)
            ))

        # Sliders del Eje X (Ajuste fino de umbrales laterales)
        if hasattr(self.ui, 'btn_x_low_minus'):
            self.ui.btn_x_low_minus.clicked.connect(lambda: self.ui.slider_x.adjust_low_thumb(-2))
            self.ui.btn_x_low_plus.clicked.connect(lambda: self.ui.slider_x.adjust_low_thumb(2))
            self.ui.btn_x_high_minus.clicked.connect(lambda: self.ui.slider_x.adjust_high_thumb(-2))
            self.ui.btn_x_high_plus.clicked.connect(lambda: self.ui.slider_x.adjust_high_thumb(2))

        # Sliders del Eje Y (Ajuste fino de umbrales verticales)
        if hasattr(self.ui, 'btn_y_low_minus'):
            self.ui.btn_y_low_minus.clicked.connect(lambda: self.ui.slider_y.adjust_low_thumb(-2))
            self.ui.btn_y_low_plus.clicked.connect(lambda: self.ui.slider_y.adjust_low_thumb(2))
            self.ui.btn_y_high_minus.clicked.connect(lambda: self.ui.slider_y.adjust_high_thumb(-2))
            self.ui.btn_y_high_plus.clicked.connect(lambda: self.ui.slider_y.adjust_high_thumb(2))

        # Guardar calibración de navegación
        if hasattr(self.ui, 'btn_nav_save'):
            self.ui.btn_nav_save.clicked.connect(lambda: self.save_navigation_requested.emit(
                self.ui.slider_x.low_thumb,
                self.ui.slider_x.high_thumb,
                self.ui.slider_y.low_thumb,
                self.ui.slider_y.high_thumb
            ))

        # ==========================================
        # 8. TUTORIAL INTERACTIVO (CRUZ)
        # ==========================================
        if hasattr(self.ui, 'btn_tut_up'):
            self.ui.btn_tut_up.clicked.connect(lambda: self.tutorial_step_clicked.emit("UP"))
            self.ui.btn_tut_down.clicked.connect(lambda: self.tutorial_step_clicked.emit("DOWN"))
            self.ui.btn_tut_left.clicked.connect(lambda: self.tutorial_step_clicked.emit("LEFT"))
            self.ui.btn_tut_right.clicked.connect(lambda: self.tutorial_step_clicked.emit("RIGHT"))


    

    def show_page(self, index):
        self.ui.stackedWidget.setCurrentIndex(index)

    def set_mapping_label(self, gesture_code, gesture_name):
        self.ui.gestureLabel.setProperty("gesture", gesture_code)
        
        # 1. Obtener la ruta absoluta del icono del gesto
        icon_path = get_asset_path(f"images/gestures/{gesture_code}.png")
        
        # 2. Normalizar las barras de la ruta para el contenedor HTML de Qt
        icon_path_html = icon_path.replace('\\', '/')
        
        # 3. Organizar el contenido: contenedor centrado, icono, salto de línea y texto
        # Aumentamos el tamaño del icono a 48x48 para que tenga más presencia al estar arriba
        rich_text = f"""
            <div align='center'>
                <img src='{icon_path_html}' width='48' height='48'>
                <br><br>
                <b>{gesture_name.upper()}</b>
            </div>
        """
        
        self.ui.gestureLabel.setText(rich_text)

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

    def update_main_video(self, pixmap, active_inputs, movement_direction, platform_name, dpad_mode):
        """
        Dibuja un HUD (Head-Up Display) sobre el video en tiempo real.
        
        El HUD muestra:
        - Estado del joystick/D-Pad (icono de movimiento actual)
        - Botones activos del gamepad (A, B, X, Y, etc.)
        
        Args:
            pixmap: QPixmap del video actual
            active_inputs: Dict[str, bool] con botones activos {'XUSB_GAMEPAD_A': True, ...}
            movement_direction: str - 'UP', 'DOWN', 'LEFT', 'RIGHT', 'IDLE'
            platform_name: str - nombre de la plataforma (para el registro de video)
            dpad_mode: bool - True si está en modo D-Pad, False si Joystick
        """
        # Crear painter para dibujar sobre el pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)  # Suavizado de líneas
        
        # 1. Parámetros de diseño del HUD
        icon_size = 80  # Tamaño de cada icono en píxeles
        spacing = 100   # Espacio entre iconos
        start_x = 20    # Margen izquierdo
        start_y = 15    # Margen superior
        frame_width = pixmap.width()  # Ancho del frame de video
        
        # 2. Cálculo dinámico de filas necesarias
        # Esto asegura que el HUD se adapte a cualquier resolución de cámara
        import math
        max_icons_per_row = max(1, int((frame_width - start_x) / spacing))
        total_icons = 1 + len(active_inputs)  # 1 joystick + N botones
        needed_rows = math.ceil(total_icons / max_icons_per_row)
        
        # Altura total del fondo negro con margen inferior
        bg_height = (needed_rows * 90) + 20
        
        # 3. Dibujar el fondo oscuro semitransparente (para que se lea el HUD sobre el video)
        painter.fillRect(0, 0, frame_width, bg_height, QColor(0, 0, 0, 140))
        
        x_offset = start_x
        y_pos = start_y
        direction_text = "dpad" if dpad_mode else "joy"  # Tipo de joystick
        
        # 4. Dibujar el icono del Joystick/D-Pad
        if movement_direction == "IDLE":
            joy_path = f"images/hud/{direction_text}_inactive.png"
        else:
            joy_path = f"images/hud/{direction_text}_{movement_direction.lower()}.png"
            
        img_joy = self._get_cached_hud_image(joy_path)
        if not img_joy.isNull():
            painter.drawImage(QPoint(x_offset, y_pos), img_joy)
            
            # Avanzar cursor y comprobar salto de línea
            x_offset += spacing
            if x_offset + icon_size > frame_width:
                x_offset = start_x
                y_pos += 90
            
        # 5. Dibujar todos los botones activos/inactivos dinámicamente
        for btn_code, is_active in active_inputs.items():
            # Limpiar el nombre: XUSB_GAMEPAD_A -> a
            clean_name = btn_code.replace("XUSB_GAMEPAD_", "").lower()
            suffix = "active" if is_active else "inactive"  # Estado visual
            
            icon_path = f"images/hud/btn_{clean_name}_{suffix}.png"
            img_btn = self._get_cached_hud_image(icon_path)
            
            if not img_btn.isNull():
                painter.drawImage(QPoint(x_offset, y_pos), img_btn)
                
                # Avanzar cursor y comprobar salto de línea
                x_offset += spacing
                if x_offset + icon_size > frame_width:
                    x_offset = start_x
                    y_pos += 90
                
        painter.end()  # Finalizar el dibujo sobre el pixmap
        
        # --- Enviar el frame pintado a la pantalla (PiP o principal) ---
        if self.pip_window and self.pip_window.isVisible():
            # Si la ventana flotante está abierta, enviarle el frame
            self.pip_window.update_image(pixmap)
        else:
            # Si no, mostrar en la etiqueta de video principal
            # Escalar el pixmap al tamaño del label (manteniendo aspecto)
            self.ui.videoLabel.setPixmap(pixmap.scaled(
                self.ui.videoLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def update_score_bar(self, score_value, is_above_threshold):
        """
        Actualiza la barra de progreso del gesto actual.
        Cambia de color dependiendo si se alcanzó el umbral de activación.
        
        Args:
            score_value: int - Valor de confianza del gesto (0-100)
            is_above_threshold: bool - True si se alcanzó el umbral de activación
        """
        # Actualizar el valor sólo si cambió (evita repainting
        if self.ui.scoreBar.value() != score_value:
            self.ui.scoreBar.setValue(score_value)

        # Leer el estado anterior de la barra (propiedad personalizada en QSS)
        current_state = self.ui.scoreBar.property("is_above_threshold") or False
        
        # Si pasó el umbral y no estaba en ese estado, repintar
        if is_above_threshold and not current_state:
            self.ui.scoreBar.setProperty("is_above_threshold", True)
            # Forzar repaint aplicando el estilo QSS de nuevo
            self.ui.scoreBar.style().unpolish(self.ui.scoreBar)
            self.ui.scoreBar.style().polish(self.ui.scoreBar)
            
        # Si cayó por debajo del umbral y estaba activado, repintar
        elif not is_above_threshold and current_state:
            self.ui.scoreBar.setProperty("is_above_threshold", False)
            # Forzar repaint aplicando el estilo QSS de nuevo
            self.ui.scoreBar.style().unpolish(self.ui.scoreBar)
            self.ui.scoreBar.style().polish(self.ui.scoreBar)

    def get_slider_threshold(self):
        """Devuelve el valor actual del slider de umbral (0-100)."""
        return self.ui.scoreSlider.value()
    
    def set_slider_threshold(self, value):
        """Establece el valor del slider de umbral al cargar una pantalla.
        
        Args:
            value: int - Valor del umbral (0-100)
        """
        self.ui.scoreSlider.setValue(value)
        self.ui.info_calib.setText(f"Umbral actual: {value}%")

    def _on_slider_value_changed(self, value):
        """Actualiza el texto informativo cada vez que cambia el slider.
        
        Args:
            value: int - Nuevo valor del slider
        """
        self.ui.info_calib.setText(f"Umbral actual: {value}%")
    def toggle_pip(self):
        """
        Alterna la ventana flotante de video (Picture-in-Picture).
        
        Returns:
            bool - True si se activó, False si se desactivó
        """
        if not self.pip_window:
            # Crear nueva ventana PiP
            self.pip_window = PipWindow()
            # Conectar el evento de cierre para limpiar la referencia
            self.pip_window.window_closed.connect(self._on_pip_closed_externally)
            self.pip_window.show()
            # Actualizar UI principal
            self.ui.videoLabel.setText("Cámara en ventana flotante")
            self.ui.pipButton.setText("Unir Cámara")
            return True
        else:
            # Cerrar la ventana existente
            self.pip_window.close()
            return False

    def _on_pip_closed_externally(self):
        """
        Restaura la interfaz cuando la ventana PiP se cierra.
        Se ejecuta tanto si el usuario hace clic en la X como si el código la cierra.
        """
        # 1. Si la ventana principal está minimizada, restaurarla
        if self.isMinimized():
            self.showNormal()  # Restaurar al tamaño anterior
            self.activateWindow()  # Traer al frente y dar foco
            
        # 2. Limpiar la referencia y restaurar textos de UI
        self.pip_window = None
        self.ui.pipButton.setText("Extraer Cámara")

    def showEvent(self, event):
        """
        Interviene justo en el momento en que la ventana se dibuja por primera vez.
        Fuerza al sistema operativo a poner la aplicación en primer plano.
        """
        super().showEvent(event)  # Ejecuta el dibujado normal de Qt
        
        # 1. Levanta físicamente la ventana por encima del resto de aplicaciones
        self.raise_()
        
        # 2. Le exige a Windows/macOS el foco activo (teclado y ratón)
        self.activateWindow()

    def closeEvent(self, event):
        """
        Maneja el evento de cierre de la ventana principal.
        Limpia recursos antes de cerrar.
        """
        # Cerrar la ventana PiP si está abierta
        if self.pip_window:
            self.pip_window.close()
        event.accept()  # Permitir el cierre
    
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


    def populate_profiles(self, profiles_list):
        """
        Genera botones dinámicos para cada perfil de control guardado.
        Utiliza una distribución en grid con icono sobre texto.
        
        Args:
            profiles_list: list[str] - Lista de nombres de archivos .json de perfiles
        """
        # 1. Limpiar completamente el grid anterior
        while self.ui.layoutProfiles.count():
            item = self.ui.layoutProfiles.takeAt(0)
            widget = item.widget()
            if widget:
                self.profile_button_group.removeButton(widget)
                widget.deleteLater()  # Destruir el widget de forma segura
                
        # Si no hay perfiles, no hacer nada más
        if not profiles_list:
            return
            
        # 2. Calcular el número ideal de columnas basado en el ancho disponible
        ancho_disponible = self.ui.scrollAreaProfiles.viewport().width()
        # Seguro anti-fallas si el widget aún no ha sido mostrado
        if ancho_disponible < 100:
            ancho_disponible = 800
        # Cada perfil ocupa ~140 píxeles de ancho
        columnas_ideales = max(1, ancho_disponible // 140)
                
        # 3. Generar los QToolButtons dinámicamente
        row, col = 0, 0
        
        # Cargar el icono de archivo (usado para todos los perfiles)
        icon_path = get_asset_path('images/file_icon.png')
        file_icon = QIcon(icon_path)

        for profile in profiles_list:
            # Limpiar el nombre del archivo: "Perfil_12-06.json" -> "PERFIL_12-06"
            clean_name = profile.replace('.json', '')
            
            # --- CREACIÓN DEL COMPONENTE ---
            btn = QToolButton()
            btn.setText(clean_name.upper())  # Mostrar en mayúsculas
            btn.setIcon(file_icon)  # Icono PNG
            btn.setIconSize(QSize(64, 64))  # Tamaño grande para visibilidad
            
            # Estilo CLAVE: Icono arriba, texto abajo (no al lado)
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Comportamiento de radio button (solo uno seleccionado a la vez)
            btn.setCheckable(True)
            btn.setProperty("filename", profile)  # Guardar el nombre original
            
            # Política de tamaño: Que crezca para llenar el espacio disponible
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumHeight(150)  # Altura mínima
            btn.setFocusPolicy(Qt.StrongFocus)  # Permitir navegación por teclado
            
            # Añadir al grupo exclusivo de botones
            self.profile_button_group.addButton(btn)
            
            # Inyectar en el layout con coordenadas (fila, columna)
            self.ui.layoutProfiles.addWidget(btn, row, col)
            
            # Calcular la siguiente posición
            col += 1
            if col >= columnas_ideales:
                col = 0  # Volver al inicio de la fila
                row += 1  # Bajar a la siguiente fila

    def _on_accept_profile(self):
        """Envía el nombre del archivo del perfil seleccionado al presentador."""
        checked_btn = self.profile_button_group.checkedButton()
        if checked_btn:
            # Emitir señal con el nombre original del archivo JSON
            self.profile_accepted.emit(checked_btn.property("filename"))

    def build_virtual_keyboard(self):
        """
        Construye un teclado virtual personalizado en una distribución de cuadrícula.
        Diseño: 13 columnas por fila para distribución uniforme.
        Soporta mayúsculas, shift y caracteres especiales.
        """
        from PySide6.QtWidgets import QPushButton, QSizePolicy

        # Flags de estado del teclado
        self.is_caps = False  # Bloq Mayúscula (permanente)
        self.is_shift = False  # Shift (temporario, se desactiva después de escribir)
        self.keyboard_buttons = []  # Lista para acceder a los botones después

        # Distribución del teclado: 13 elementos por fila para equilibrio visual
        # Nota: Los caracteres especiales se muestran en la fila, Shift modifica su apariencia
        teclas = [
            ['º', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '?', '¡'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '`', '+'],
            ['BLOQ', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ', '´', 'Ç'],
            ['SHIFT', '<', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-', 'SHIFT'],
            ['ESPACIO']  # Fila especial que ocupa todo el ancho
        ]
        
        # Crear botones y añadirlos al layout
        for row_idx, fila in enumerate(teclas):
            for col_idx, tecla in enumerate(fila):
                btn = QPushButton()
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumHeight(60)
                
                if tecla == 'ESPACIO':
                    # El botón de espacio ocupa todas las 13 columnas
                    self.ui.keyboardGridLayout.addWidget(btn, row_idx, 0, 1, 13)
                else:
                    # Botones normales en su celda del grid
                    self.ui.keyboardGridLayout.addWidget(btn, row_idx, col_idx)

                # Conectar el evento de clic con el manejador
                btn.clicked.connect(lambda checked=False, char=tecla: self._on_key_pressed(char))
                # Guardar referencia al botón y su carácter base
                self.keyboard_buttons.append({'btn': btn, 'base': tecla})

        # Actualizar los labels de los botones según el estado actual
        self._update_keyboard_labels()

    def _update_keyboard_labels(self):
        """
        Actualiza los labels de los botones del teclado según el estado.
        Cambia mayúsculas/minúsculas basado en Shift y Bloq Mayúscula.
        """
        # Mapa de caracteres Shift (los caracteres que se muestran cuando Shift está activado)
        shift_map = {
            'º': 'ª', '1': '!', '2': '"', '3': '·', '4': '$', '5': '%', '6': '&&', '7': '/',
            '8': '(', '9': ')', '0': '=', '?': "'", '¡': '¿',
            '`': '^', '+': '*', '´': '¨', '<': '>', ',': ';', '.': ':', '-': '_'
        }

        # Recorrer todos los botones del teclado
        for item in self.keyboard_buttons:
            btn = item['btn']
            base = item['base']  # Carácter base (tal como fue definido)

            # Teclas de control (no se alteran con Shift/Mayúscula)
            if base in ['BLOQ', 'SHIFT', 'ESPACIO', 'TAB']:
                btn.setText(base)  # Mostrar el nombre tal cual
                # Cambiar color de fondo si está activada
                if base == 'BLOQ':
                    btn.setStyleSheet("background-color: #0078D7; border-color: #ffffff;" if self.is_caps else "")
                elif base == 'SHIFT':
                    btn.setStyleSheet("background-color: #0078D7; border-color: #ffffff;" if self.is_shift else "")
            
            # Letras básicas (a-z, A-Z)
            elif base.isalpha() and len(base) == 1 and base != 'º':
                # Cambiar caso: XOR lógica (si uno está encendido pero no ambos)
                if self.is_caps ^ self.is_shift:
                    btn.setText(base.upper())
                else:
                    btn.setText(base.lower())
            
            # Números y símbolos especiales
            else:
                if self.is_shift:
                    # Si Shift está activado, mostrar el carácter modificado
                    btn.setText(shift_map.get(base, base))
                else:
                    # Si no, mostrar el carácter base
                    btn.setText(base)
                
            

    def _on_key_pressed(self, char):
        """
        Procesa la pulsación de una tecla del teclado virtual.
        Maneja:
        - Escritura de caracteres normales
        - Activación de Bloq Mayúscula y Shift
        - Inserción de espacios y tabuladores
        
        Args:
            char: str - Carácter o comando de tecla presionado
        """
        current_text = self.ui.keyboardDisplay.text()
        
        if char == 'BLOQ':
            # Alternar el Bloq Mayúscula permanente
            self.is_caps = not self.is_caps
            self._update_keyboard_labels()
            return
            
        elif char == 'SHIFT':
            # Alternar el Shift temporal
            self.is_shift = not self.is_shift
            self._update_keyboard_labels()
            return
            
        elif char == 'ESPACIO':
            # Insertar espacio (máximo 30 caracteres)
            self.is_default_text_untouched = False  # El usuario ha tocado el texto
            if len(current_text) < 30:
                self.ui.keyboardDisplay.setText(current_text + " ")
                
        elif char == 'TAB':
            # Insertar tabulación (4 espacios)
            self.is_default_text_untouched = False
            if len(current_text) < 30:
                self.ui.keyboardDisplay.setText(current_text + "    ")
                
        else:
            # Insertar carácter normal
            self.is_default_text_untouched = False
            if len(current_text) < 30:
                # Recuperar el texto pintado en el botón (puede estar modificado por Shift)
                for item in self.keyboard_buttons:
                    if item['base'] == char:
                        char_to_write = item['btn'].text()
                        # Corrección para mostrar '&' en lugar de '&&' (conflicto con Qt)
                        if char_to_write == '&&':
                            char_to_write = '&'
                        self.ui.keyboardDisplay.setText(current_text + char_to_write)
                        break

        # Desactivar el Shift después de escribir un carácter normal
        # (Los Shift-temporarios se desactivan automáticamente después de cada pulsación)
        if self.is_shift and char not in ['BLOQ', 'SHIFT', 'TAB']:
            self.is_shift = False
            self._update_keyboard_labels()

    def open_virtual_keyboard(self, default_text=""):
        """
        Abre el teclado virtual con un texto por defecto sugerido.
        
        Args:
            default_text: str - Texto sugerido (p. ej., nombre auto-generado para perfil)
        """
        self.ui.keyboardDisplay.setText(default_text)
        self.is_shift = False
        self.is_caps = False
        # Marcar si el texto es el por defecto sin modificación del usuario
        self.is_default_text_untouched = bool(default_text)
        self._update_keyboard_labels()
        # Mostrar la página del teclado en el stacked widget
        self.show_page(4)

    def _on_keyboard_backspace(self):
        """
        Maneja la pulsación del botón backspace del teclado virtual.
        Si el texto es el por defecto sin tocar, lo borra completamente.
        Si ya ha sido modificado, borra única letra al final.
        """
        if getattr(self, 'is_default_text_untouched', False):
            # Si el usuario no ha tocado el texto, borrarlo completamente
            self.ui.keyboardDisplay.setText("")
            self.is_default_text_untouched = False  # Marcar como modificado
        else:
            # Si ya ha sido modificado, borrar la última letra
            texto_actual = self.ui.keyboardDisplay.text()
            self.ui.keyboardDisplay.setText(texto_actual[:-1])

    def _on_keyboard_accept(self):
        """
        Envía el texto capturado al presentador cuando el usuario presiona 'Aceptar'.
        """
        filename = self.ui.keyboardDisplay.text().strip()  # Eliminar espacios al inicio/final
        if filename:  # Sólo si no está vacío
            self.save_as_requested.emit(filename)


    def populate_explorer(self, current_path, items_list, mode="FOLDER", page_index_return=None):
        """
        Genera botones interactivos para el explorador de archivos.
        
        Args:
            current_path: str - Ruta actual del directorio
            items_list: list[tuple(str, str)] - Lista de items (nombre, tipo)
                        Tipos: "folder" o "exe"
            mode: str - Modo del explorador: "FOLDER" o "EMULATOR"
            page_index_return: int - Página a la que volver después
        """
        # Mostrar la ruta actual en el UI
        self.ui.label_explorer_path.setText(f"Ruta actual: {current_path}")
        
        # Limpiar completamente el layout anterior
        while self.ui.layoutExplorer.count():
            item = self.ui.layoutExplorer.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Adaptar el texto del botón de selección según el modo
        if mode == "FOLDER":
            self.ui.explorerSelectButton.setText("✅ ELEGIR ESTA CARPETA")
        elif mode == "EMULATOR":
            self.ui.explorerSelectButton.setText("🖥️ PREDETERMINADO WINDOWS")

        # Calcular el número ideal de columnas
        ancho_disponible = self.ui.scrollAreaExplorer.viewport().width()
        if ancho_disponible < 100:
            ancho_disponible = 800  # Seguro anti-fallas
        ideal_columns = max(1, ancho_disponible // 140)
        row, col = 0, 0
        
        # Cargar iconos
        folder_icon = QIcon(get_asset_path('images/folder_icon.png'))
        emulator_icon = QIcon(get_asset_path('images/emulator_icon.png'))
        
        # items_list contiene tuplas: (nombre_archivo, tipo_archivo)
        for item_name, item_type in items_list:
            btn = QToolButton()
            # Envolver el texto en múltiples líneas si es muy largo
            multiline_text = textwrap.fill(item_name, width=12)
            btn.setText(multiline_text)
            
            btn.setIconSize(QSize(60, 60))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFocusPolicy(Qt.StrongFocus)
            
            # Conectar señales diferentes basado en el tipo de archivo
            if item_type == "folder":
                # Carpeta: emitir señal de entrada en directorio
                btn.clicked.connect(lambda checked=False, f=item_name: self.explorer_folder_clicked.emit(f))
                btn.setIcon(folder_icon)
            elif item_type == "exe":
                # Ejecutable: emitir señal de selección de emulador
                btn.clicked.connect(lambda checked=False, f=item_name: self.emulator_exe_chosen.emit(f, page_index_return))
                btn.setIcon(emulator_icon)
            
            self.ui.layoutExplorer.addWidget(btn, row, col)
            
            col += 1
            if col >= ideal_columns:
                col = 0
                row += 1


    def populate_emulator_settings(self, emulators_dict):
        """
        Genera filas dinámicas con la configuración de cada emulador.
        Cada fila: [Nombre Consola] [Botón Para Elegir Emulador]
        
        Args:
            emulators_dict: dict[str, str] - {"Consola": "ruta_ejecutable_o_Default", ...}
        """
        layout = self.ui.layoutDynamicEmulators
        
        # --- LIMPIEZA PROFUNDA del layout anterior ---
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()  # Destruir widget
            elif item.layout():
                # Si es un sublayout (fila), destruir sus componentes primero
                sub_layout = item.layout()
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget:
                        sub_widget.deleteLater()
                sub_layout.deleteLater()  # Destruir el sublayout vacío
            elif item.spacerItem():
                layout.removeItem(item)  # Remover espaciadores

        # Título de la sección
        title_lbl = QLabel("CONFIGURACIÓN DE EMULADORES")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        # Crear filas dinámicas para cada consola
        for console, current_emu in emulators_dict.items():
            row_layout = QHBoxLayout()
            
            # Columna 1: Nombre de la consola
            console_lbl = QLabel(console)
            console_lbl.setMinimumWidth(150)
            font_lbl = QFont()
            font_lbl.setPointSize(12)
            console_lbl.setFont(font_lbl)
            
            # Columna 2: Botón para seleccionar/cambiar emulador
            btn = QPushButton()
            btn.setMinimumHeight(50)
            
            # Si el emulador es una ruta válida, mostrar sólo el nombre del archivo
            # Si es "Default" o ruta inválida, mostrar el texto tal cual
            if current_emu != "Default" and os.path.exists(current_emu):
                display_text = os.path.basename(current_emu)
            elif current_emu == "Default":
                display_text = "Predeterminado"
            else:
                display_text = current_emu
                
            btn.setText(display_text)
            # Conectar con el presentador para que el usuario pueda cambiar el emulador
            btn.clicked.connect(lambda checked=False, c=console: self.emulator_setup_requested.emit(c, 8))
            
            # Añadir ambas columnas a la fila
            row_layout.addWidget(console_lbl)
            row_layout.addWidget(btn)
            layout.addLayout(row_layout)
            
        # Añadir espacio al final para empujar todo hacia arriba
        layout.addStretch()


    def populate_platforms_catalog(self, platforms_list):
        """
        Genera botones dinámicos para cada plataforma de juegos.
        
        Args:
            platforms_list: list[str] - Nombres de plataformas ("Steam", "NES", "SNES", etc.)
        """
        # 1. Limpiar el contenedor por si había botones viejos
        while self.ui.layoutPlatforms.count():
            item = self.ui.layoutPlatforms.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. Calcular el número ideal de columnas
        ancho_disponible = self.ui.scrollAreaPlaforms.viewport().width()
        if ancho_disponible < 100:
            ancho_disponible = 800  # Seguro anti-fallas
        max_columnas = max(1, ancho_disponible // 140)
        fila = 0
        columna = 0

        # 3. Crear botones para cada plataforma
        for platform_name in platforms_list:
            btn = QToolButton()
            btn.setText(platform_name)
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Opcional: Asignar icono personalizado por plataforma
            # if platform_name == "Steam": btn.setIcon(QIcon("rutas/steam.png"))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Conectar evento: cuando se hace clic, emitir señal con el nombre de la plataforma
            btn.clicked.connect(lambda checked=False, p=platform_name: self.platform_selected.emit(p))
            
            # 4. Añadir el botón al grid en la posición calculada
            self.ui.layoutPlatforms.addWidget(btn, fila, columna)
            
            # 5. Calcular la siguiente posición
            columna += 1
            if columna >= max_columnas:
                columna = 0  # Volver al inicio de la fila
                fila += 1  # Bajar a la siguiente fila


    def populate_games_catalog(self, games_list, platform_name, emulator_name=None):
        """
        Genera botones dinámicos para los juegos de una plataforma.
        Cada botón contiene título e icono (portada) del juego.
        
        Args:
            games_list: list[dict] - Lista de juegos con keys: 'title', 'exe_path', 'icon'
            platform_name: str - Nombre de la plataforma (para el UI y conexiones)
            emulator_name: str - Ruta del emulador (opcional, usado para algunas plataformas)
        """
        # Actualizar el título mostrando la plataforma seleccionada
        self.ui.platformLabel.setText(f"Plataforma: {platform_name}")
        
        # Adaptar los botones visibles según la plataforma
        if platform_name == "Steam":
            # Steam: ocultar emulador, mostrar botón de escaneo de Steam
            self.ui.gamesEmulatorsButton.hide()
            self.ui.steamGamesScanButton.show()
            self.ui.gamesScanFolderButton.hide()
        else:
            # Otras plataformas: mostrar botón de escaneo de carpeta
            self.ui.steamGamesScanButton.hide()
            self.ui.gamesScanFolderButton.show()
            # Si hay emulador, mostrar su nombre
            if emulator_name is not None:
                self.ui.gamesEmulatorsButton.show()
                # Extraer sólo el nombre del archivo sin ruta ni extensión
                emulator_name=os.path.splitext(os.path.basename(emulator_name))[0].upper()
                if emulator_name=="DEFAULT":
                    emulator_name="PREDETERMINADO"
                self.ui.gamesEmulatorsButton.setText(f"Emulador:\n{emulator_name}")
                try:
                    # Limpiar cualquier conexión previa para evitar duplicados
                    self.ui.gamesEmulatorsButton.clicked.disconnect()
                except (RuntimeError, TypeError):
                    # Si no tenía conexiones previas, ignorar el error de Qt
                    pass
                
                # Conectar con el presentador para cambiar emulador si es necesario
                self.ui.gamesEmulatorsButton.clicked.connect(
                    lambda checked=False: self.emulator_setup_requested.emit(platform_name, 5)
                )

        # Limpiar completamente el layout de juegos
        while self.ui.layoutGames.count():
            item = self.ui.layoutGames.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Si no hay juegos, terminar aquí
        if not games_list:
            return

        # Calcular el número ideal de columnas
        ancho_disponible = self.ui.scrollAreaGame.viewport().width()
        if ancho_disponible < 100:
            ancho_disponible = 800  # Seguro anti-fallas
        columnas_ideales = max(1, ancho_disponible // 140)
        # Icono por defecto si el juego no tiene portada
        icono_defecto = QIcon(get_asset_path('game_default.png'))

        row, col = 0, 0

        # Crear botones para cada juego
        for juego in games_list:
            # Extraer datos del juego
            titulo_crudo = juego.get("title", "JUEGO DESCONOCIDO").upper()
            exe_path = juego.get("exe_path", "")
            
            # Envolver el título en múltiples líneas si es muy largo
            titulo_multilinea = textwrap.fill(titulo_crudo, width=12)
            
            # Crear botón
            btn = QToolButton()
            btn.setText(titulo_multilinea)
            
            # Asignar icono (portada del juego)
            ruta_icono = juego.get("icon")
            btn.setIcon(QIcon(get_asset_path(ruta_icono)) if ruta_icono else icono_defecto)
            btn.setIconSize(QSize(87.5, 70))  # Tamaño de portada
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setFocusPolicy(Qt.StrongFocus)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Conectar evento de clic con la señal de lanzamiento
            btn.clicked.connect(lambda checked=False, path=exe_path: self.game_launch_requested.emit(path))
            
            # Añadir el botón al grid
            self.ui.layoutGames.addWidget(btn, row, col)
            
            # Calcular la siguiente posición
            col += 1
            if col >= columnas_ideales:
                col = 0
                row += 1

    def show_controller_image(self, image_path):
        """
        Carga y muestra una imagen de controlador (p. ej., diagrama de botones).
        Usa técnica de escalado inteligente para adaptarse al tamaño real del widget.
        
        Args:
            image_path: str - Ruta relativa a la imagen (ej: "images/nes_controller.png")
        """
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import QTimer
        from model import get_asset_path
        
        # Guardar la ruta para posibles cálculos posteriores
        self.current_controller_path = image_path
        ruta_absoluta = get_asset_path(image_path)
        
        # 1. Guardar la imagen original en la RAM (no releer del disco en cada redimensionado)
        self._pixmap_original = QPixmap(ruta_absoluta)
        
        if not self._pixmap_original.isNull():
            # 2. Desactivar el escalado automático y mostrar el widget
            self.ui.controllerImage.setScaledContents(False)
            self.ui.controllerImage.show()
            
            # 3. MAGIA: Programar el escalado para cuando el Layout termine de calcularse
            # QTimer.singleShot(0, ...) ejecuta la función en el siguiente ciclo de eventos
            QTimer.singleShot(0, self._apply_controller_scaling)

    def _apply_controller_scaling(self):
        """
        Aplica el escalado de la imagen usando el ancho real calculado por el Layout.
        Mantiene la relación de aspecto original.
        """
        from PySide6.QtCore import Qt
        
        # Verificar que tenemos la imagen original cargada
        if hasattr(self, '_pixmap_original') and not self._pixmap_original.isNull():
            # Obtener el ancho real del widget (ya calculado por el Layout)
            ancho_real = self.ui.controllerImage.width()
            
            # Escalar la imagen manteniendo la relación de aspecto
            pixmap_escalado = self._pixmap_original.scaledToWidth(ancho_real, Qt.SmoothTransformation)
            
            # Alinear la imagen en la parte superior y centrada
            self.ui.controllerImage.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.ui.controllerImage.setPixmap(pixmap_escalado)

    def hide_controller_image(self):
        """Oculta la imagen del controlador del UI."""
        self.ui.controllerImage.hide()

    def resizeEvent(self, event):
        """
        Maneja el evento de redimensionado de la ventana principal.
        Recalcula el escalado de la imagen si está visible.
        """
        super().resizeEvent(event)  # Llamar al comportamiento base
        
        # Si la imagen está visible, recalcular su tamaño
        if hasattr(self, 'ui') and self.ui.controllerImage.isVisible() and self.current_controller_path:
            self._apply_controller_scaling()

    def _get_cached_hud_image(self, relative_path):
        """
        Obtiene una imagen del cache en RAM o la carga/escala si es la primera vez.
        Esto optimiza el rendimiento durante la transmisión de video en tiempo real.
        
        Args:
            relative_path: str - Ruta relativa de la imagen (ej: "images/hud/joy_up.png")
            
        Returns:
            QImage - Imagen escalada a 80x80 píxeles
        """
        if relative_path not in self.hud_image_cache:
            # Primera vez que se accede: cargar del disco y pre-escalar
            full_path = get_asset_path(relative_path)
            img = QImage(full_path)
            
            if not img.isNull():
                # Guardar en cache ya escalada a 80x80 para no consumir CPU en cada frame
                self.hud_image_cache[relative_path] = img.scaled(
                    80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            else:
                # Si el archivo no existe, guardar una imagen vacía para evitar intentos repetidos
                self.hud_image_cache[relative_path] = QImage()
                
        return self.hud_image_cache[relative_path]
    
    def update_navigation_sliders(self, val_x, val_y):
        """
        Actualiza los sliders de calibración de navegación en tiempo real.
        Muestra donde está el cursor actual del usuario.
        
        Args:
            val_x: float - Valor X del cursor (0.0 a 1.0)
            val_y: float - Valor Y del cursor (0.0 a 1.0)
        """
        if hasattr(self.ui, 'slider_x') and hasattr(self.ui, 'slider_y'):
            self.ui.slider_x.set_current_value(val_x)
            self.ui.slider_y.set_current_value(val_y)

    def set_navigation_thumbs(self, low_x, high_x, low_y, high_y):
        """
        Posiciona los "thumbs" (controles deslizantes) al abrir la pantalla de calibración.
        Estos definen los límites de navegación.
        
        Args:
            low_x, high_x: Umbrales mínimo y máximo del eje X
            low_y, high_y: Umbrales mínimo y máximo del eje Y
        """
        if hasattr(self.ui, 'slider_x') and hasattr(self.ui, 'slider_y'):
            # Slider X
            self.ui.slider_x.low_thumb = low_x
            self.ui.slider_x.high_thumb = high_x
            self.ui.slider_x.update()  # Repintar
            
            # Slider Y
            self.ui.slider_y.low_thumb = low_y
            self.ui.slider_y.high_thumb = high_y
            self.ui.slider_y.update()  # Repintar

    def changeEvent(self, event):
        """
        Detecta cambios en el estado de la ventana (minimizar, restaurar, etc.).
        Cierra la ventana PiP si la ventana principal se restaura (de minimizado).
        
        Args:
            event: QEvent - Evento de cambio de estado
        """
        # Verificar si es un evento de cambio de estado de ventana
        if event.type() == QEvent.WindowStateChange:
            # Comprobar si la ventana ya NO está minimizada (es decir, se ha restaurado)
            if not (self.windowState() & Qt.WindowMinimized):
                # Si la ventana PiP está abierta, cerrarla
                if getattr(self, 'pip_window', None) is not None:
                    self.pip_window.close()
                    # Nota: Al hacer .close(), saltara automáticamente el método
                    # _on_pip_closed_externally, que se encargara de la limpieza
                    
        # Siempre llamar al método original para no romper Qt
        super().changeEvent(event)

    # En view.py
    def populate_gesture_catalog(self, gestures_dict):
        """Genera dinámicamente los botones basándose exclusivamente en los datos recibidos."""
        # Vaciamos el layout viejo
        while self.ui.gridLayout_2.count():
            item = self.ui.gridLayout_2.takeAt(0)
            widget = item.widget()
            if widget:
                self.ui.gestureButtons.removeButton(widget)
                widget.deleteLater()

        row, col = 0, 0
        for code, name in gestures_dict.items():
            # 1. Usamos QToolButton en lugar de QPushButton
            btn = QToolButton()
            btn.setText(name)
            
            # 2. Hacemos el icono mucho más grande (puedes ajustar este 80, 80 a tu gusto)
            btn.setIconSize(QSize(80, 80))
            
            # 3. Posicionamos el texto justo debajo del icono
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Mantenemos el resto de tus configuraciones
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
            btn.setIcon(QIcon(get_asset_path(f"images/gestures/{code}.png"))) 
            btn.setProperty("gesture", code)
            
            btn.clicked.connect(lambda checked=False, b=btn: self.gesture_selected.emit(b))
            
            self.ui.gestureButtons.addButton(btn)
            self.ui.gridLayout_2.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

    def set_onboarding_mode(self, enabled):
        """
        Activa/desactiva el modo tutorial mostrando/ocultando ciertos botones.
        Durante el tutorial, se ocultan los botones que distraen al usuario.
        
        Args:
            enabled: bool - True para activar modo tutorial, False para desactivarlo
        """
        # Ocultar/mostrar botones de navegación y guardado
        self.ui.gesturesBackButton.setVisible(not enabled)
        self.ui.gesturesLoadButton.setVisible(not enabled)
        self.ui.gesturesSaveLocalButton.setVisible(not enabled)
        
        # Ocultar/mostrar botones de video para que no distraigan
        self.ui.pipButton.setVisible(not enabled)
        self.ui.stopButton.setVisible(not enabled)

    def show_tutorial_message(self, title, message):
        """
        Muestra un cuadro de diálogo informativo que bloquea la aplicación hasta que se lea.
        
        Args:
            title: str - Título del diálogo
            message: str - Mensaje a mostrar
        """
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        # Estilo para que se adapte al tema oscuro
        msg.setStyleSheet("QLabel{ min-width: 400px; font-size: 14px; }")
        msg.exec()  # Bloquear hasta que el usuario haga clic en OK

    def setup_tutorial_step(self, target_direction):
        """
        Configura visualmente el paso del tutorial.
        Destaca el botón objetivo y opaca los demás.
        
        Args:
            target_direction: str - Dirección objetivo ("UP", "DOWN", "LEFT", "RIGHT")
        """
        buttons = {
            "UP": self.ui.btn_tut_up,
            "DOWN": self.ui.btn_tut_down,
            "LEFT": self.ui.btn_tut_left,
            "RIGHT": self.ui.btn_tut_right
        }

        for direction, btn in buttons.items():
            # TODOS los botones deben ser interactuables siempre
            btn.setEnabled(True)
            
            if direction == target_direction:
                # Botón objetivo: azul primario con borde verde cuando tiene foco
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078D7; 
                        color: white; 
                        border: 2px solid #005a9e;
                        border-radius: 15px;
                    }
                    QPushButton:focus {
                        border: 3px solid #00FF00;
                        background-color: #0086f0;
                        outline: none;
                    }
                """)
            else:
                # Botón inactivo: gris oscuro con borde punteado
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e; 
                        color: #555555; 
                        border: 2px dashed #444444;
                        border-radius: 15px;
                    }
                    QPushButton:focus {
                        border: 3px solid #00FF00;
                        background-color: #2b2b2b;
                        outline: none;
                    }
                """)

    def update_tutorial_icon(self, target_direction):
        """
        Actualiza el icono central del tutorial cuando el usuario mueve el foco.
        Cambia de icono cuando el foco está en el botón objetivo.
        
        Args:
            target_direction: str - Dirección objetivo para este paso
        """
        from PySide6.QtWidgets import QApplication
        
        # Obtener qué widget tiene el foco actualmente
        focused_widget = QApplication.focusWidget()
        
        buttons = {
            "UP": self.ui.btn_tut_up,
            "DOWN": self.ui.btn_tut_down,
            "LEFT": self.ui.btn_tut_left,
            "RIGHT": self.ui.btn_tut_right
        }
        
        target_btn = buttons.get(target_direction)
        
        # Si el foco está en el botón objetivo, mostrar una sonrisa (gesto confirmado)
        if focused_widget == target_btn:
            icon_path = get_asset_path("images/gestures/smile.png")
        else:
            # Si no, mostrar el icono de movimiento (indicar la dirección)
            icon_path = get_asset_path("images/gestures/movement.png")
            
        # Escalar el icono a 120x120 píxeles
        pixmap = QPixmap(icon_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.icon_tut_info.setPixmap(pixmap)