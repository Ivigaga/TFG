import os

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QButtonGroup, QToolButton, QSizePolicy
from PySide6.QtGui import QColor, QIcon, QAction, QImage, QPainter, QPixmap
from PySide6.QtCore import QEvent, QPoint, Signal, Qt, QSize
from PySide6.QtUiTools import QUiLoader

from model import get_asset_path
from prueba_ui import Ui_MainWindow
import math
import textwrap

class PipWindow(QWidget):
    # 1. Nueva señal para avisar de que la ventana muere
    window_closed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video PiP")
        self.resize(400, 300)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.move(0, 0)
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

    # 2. Capturamos cuando el usuario le da a la 'X' de Windows
    def closeEvent(self, event):
        self.window_closed.emit() # Gritamos que nos estamos cerrando
        super().closeEvent(event) # Dejamos que Windows termine de destruirla


class MainView(QMainWindow):
    # Custom Signals to notify the Presenter
    pip_toggled = Signal()
    video_control_toggled = Signal()
    navigation_requested = Signal(int)  # Sends the page index
    gesture_selected = Signal(object)      # Sends the gesture button object
    stop_reading_score = Signal()
    save_controls = Signal(str, str, int)  # gesture_code, input_code, threshold
    save_mapping_current = Signal()  # Signal to save the mapping on already loaded file
    load_profiles_requested = Signal()
    profile_accepted = Signal(str)
    save_as_requested = Signal(str) # Envía el nombre del nuevo archivo

    games_catalog_requested = Signal()
    scan_games_requested = Signal()
    game_launch_requested = Signal(str)  # Envía la ruta o URI del juego seleccionado

    # Señales del Explorador de Archivos
    explorer_opened = Signal()
    explorer_folder_clicked = Signal(str)
    explorer_up_clicked = Signal()
    explorer_select_clicked = Signal()

    # New Signals for Emulator Settings
    emulator_settings_opened = Signal()
    emulator_setup_requested = Signal(str,int) # Sends the console name
    emulator_exe_chosen = Signal(str,int)      # Sends the chosen .exe filename
    explorer_cancel_clicked = Signal()     # Replaces the hardcoded cancel

    platform_selected = Signal(str)
    remove_platform = Signal()  # Nueva señal para eliminar la plataforma filtrada y volver a mostrar todo

    controls_opened = Signal()
    controls_closed = Signal()

    navigation_settings_opened = Signal()
    save_navigation_requested = Signal(int, int, int, int) # low_x, high_x, low_y, high_y
    
    selectedNavigationMode = Signal(bool) # False para Joystick, True para D-Pad

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Gesture Control - MVP Architecture")
        self.resize(1020, 751)

        self.ui.stackedWidget.setCurrentIndex(0)
        # --- EL TRUCO DEL FANTASMA PARA NO ROMPER EL LAYOUT ---
        # 1. Capturamos las reglas de tamaño que tiene la imagen del mando
        policy = self.ui.controllerImage.sizePolicy()
        self.hud_image_cache = {}
        # 2. Le ordenamos a Qt que MANTENGA el hueco físico aunque se oculte el componente
        policy.setRetainSizeWhenHidden(True)
        self.ui.controllerImage.setSizePolicy(policy)
        
        # 3. Ahora sí podemos ocultarlo de forma 100% segura. El vídeo no se inmutará.
        self.ui.controllerImage.hide()
        self.current_controller_path = "" 
        
        # 4. (Opcional pero recomendado) Apagamos el tirano del vídeo por si acaso
        self.ui.videoLabel.setScaledContents(False)
        # -------------------------------------------------------

        self.pip_window = None
        self._connect_signals()
        

    def _connect_signals(self):
        """Connects UI events to our custom Signals."""
        # Video controls
        self.ui.pipButton.clicked.connect(self.pip_toggled.emit)
        self.ui.stopButton.clicked.connect(self.video_control_toggled.emit)
        
        # Navigation
        #self.ui.changeControlsButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.ui.stackedWidgetAcciones.setCurrentIndex(0))
        self.ui.controlsCancelButton.clicked.connect(self.stop_reading_score.emit)
        

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
        self.ui.gesturesSaveLocalButton.clicked.connect(self.save_mapping_current.emit) 
        
        # Escuchar clics en las opciones para iluminar la categoría en tiempo real
        self.ui.controlButtons.buttonClicked.connect(self._on_action_button_clicked)

        # --- CONTROL DINÁMICO DEL SLIDER Y UMBRALES ---
        # Sincronizar el texto informativo con el valor real del slider
        self.ui.scoreSlider.valueChanged.connect(self._on_slider_value_changed)
        
        # Hacer que los botones masivos incrementen o decrementen el slider
        self.ui.btn_plus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() + 5))
        self.ui.btn_minus.clicked.connect(lambda: self.ui.scoreSlider.setValue(self.ui.scoreSlider.value() - 5))

        self.ui.gesturesLoadButton.clicked.connect(self.load_profiles_requested.emit)
        
        # Grupo exclusivo para los botones de perfiles (actúan como Radio Buttons)
        self.profile_button_group = QButtonGroup(self)
        self.profile_button_group.setExclusive(True)
        
        self.ui.loadBackButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.loadAcceptButton.clicked.connect(self._on_accept_profile)

        # El botón de "Guardar Archivo" del catálogo ahora abre el teclado (Página 4)
        self.ui.gesturesSaveExternalButton.clicked.connect(self.open_virtual_keyboard)
        
        # Controles del teclado
        self.ui.keyboardCancelButton.clicked.connect(lambda: self.navigation_requested.emit(1))
        self.ui.keyboardBackspaceButton.clicked.connect(self._on_keyboard_backspace)
        self.ui.keyboardAcceptButton.clicked.connect(self._on_keyboard_accept)
        
        # Construimos el teclado al iniciar
        self.build_virtual_keyboard()

        self.ui.gamesBackButton.clicked.connect(self.remove_platform.emit)
        self.ui.gamesScanButton.clicked.connect(self.scan_games_requested.emit)

        # Controles de las páginas de ajustes
        self.ui.settingsBackButton.clicked.connect(lambda: self.navigation_requested.emit(0))
        self.ui.emulatorSettingsBackButton.clicked.connect(lambda: self.navigation_requested.emit(0))
        # Controles del explorador
        self.ui.scanFolderButton.clicked.connect(self.explorer_opened.emit)
        self.ui.gamesScanFolderButton.clicked.connect(self.explorer_opened.emit)
        self.ui.explorerUpButton.clicked.connect(self.explorer_up_clicked.emit)
        self.ui.explorerSelectButton.clicked.connect(self.explorer_select_clicked.emit)


        #self.ui.settingsButton.clicked.connect(lambda: self.navigation_requested.emit(7))
        self.ui.pushButton.clicked.connect(self.emulator_settings_opened.emit)
        self.ui.explorerCancelButton.clicked.connect(self.explorer_cancel_clicked.emit) 


        self.ui.emulatorsButton.clicked.connect(self.emulator_settings_opened.emit)
        
        # Sustituye las líneas antiguas de estos botones por estas:
        self.ui.controlsButton.clicked.connect(self.controls_opened.emit)
        self.ui.gamesControlsButton.clicked.connect(self.controls_opened.emit)
        self.ui.gesturesBackButton.clicked.connect(self.controls_closed.emit)

        self.ui.noseButton.clicked.connect(lambda: self.navigation_requested.emit(9))

        if hasattr(self.ui, 'btn_nav_back'):
            self.ui.btn_nav_back.clicked.connect(lambda: self.navigation_requested.emit(
                self.ui.stackedWidget.indexOf(self.ui.gesturesPage)
            ))

        # --- Controles del Slider del Eje X ---
        if hasattr(self.ui, 'btn_x_low_minus'):
            self.ui.btn_x_low_minus.clicked.connect(lambda: self.ui.slider_x.adjust_low_thumb(-2))
            self.ui.btn_x_low_plus.clicked.connect(lambda: self.ui.slider_x.adjust_low_thumb(2))
            self.ui.btn_x_high_minus.clicked.connect(lambda: self.ui.slider_x.adjust_high_thumb(-2))
            self.ui.btn_x_high_plus.clicked.connect(lambda: self.ui.slider_x.adjust_high_thumb(2))

        # --- Controles del Slider del Eje Y ---
        if hasattr(self.ui, 'btn_y_low_minus'):
            self.ui.btn_y_low_minus.clicked.connect(lambda: self.ui.slider_y.adjust_low_thumb(-2))
            self.ui.btn_y_low_plus.clicked.connect(lambda: self.ui.slider_y.adjust_low_thumb(2))
            self.ui.btn_y_high_minus.clicked.connect(lambda: self.ui.slider_y.adjust_high_thumb(-2))
            self.ui.btn_y_high_plus.clicked.connect(lambda: self.ui.slider_y.adjust_high_thumb(2))

        self.ui.noseButton.clicked.connect(self.navigation_settings_opened.emit)

        if hasattr(self.ui, 'btn_nav_save'):
            self.ui.btn_nav_save.clicked.connect(lambda: self.save_navigation_requested.emit(
                self.ui.slider_x.low_thumb,
                self.ui.slider_x.high_thumb,
                self.ui.slider_y.low_thumb,
                self.ui.slider_y.high_thumb
            ))
        self.ui.btn_nav_joystick.clicked.connect(lambda: self.selectedNavigationMode.emit(False))
        self.ui.btn_nav_dpad.clicked.connect(lambda: self.selectedNavigationMode.emit(True))
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

    def update_main_video(self, pixmap, active_inputs, movement_direction, platform_name, dpad_mode):
        """Overlays real-time HUD inputs on top of the camera frame using RAM cache."""
        from PySide6.QtGui import QPainter, QColor
        from PySide6.QtCore import QPoint, Qt
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent dark overlay for better HUD visibility
        painter.fillRect(0, 0, pixmap.width(), 70, QColor(0, 0, 0, 140))
        
        x_offset = 20
        y_pos = 15
        direction_text="dpad" if dpad_mode else "joy"
        # 1. Draw Joystick/Movement status
        if movement_direction == "IDLE":
            joy_path = f"images/hud/{direction_text}_inactive.png"
        else:
            joy_path = f"images/hud/{direction_text}_{movement_direction.lower()}.png"
            
        img_joy = self._get_cached_hud_image(joy_path)
        if not img_joy.isNull():
            painter.drawImage(QPoint(x_offset, y_pos), img_joy)
            x_offset += 60
            
        # 2. Draw active/inactive buttons dynamically
        for btn_code, is_active in active_inputs.items():
            clean_name = btn_code.replace("XUSB_GAMEPAD_", "").lower()
            suffix = "active" if is_active else "inactive"
            
            # Handle platform-specific naming for back and start buttons
            if clean_name in ["back", "start"] and platform_name:
                platform_slug = platform_name.lower().replace(" ", "_")
                icon_path = f"images/hud/btn_{clean_name}_{platform_slug}_{suffix}.png"
            else:
                icon_path = f"images/hud/btn_{clean_name}_{suffix}.png"
            
            img_btn = self._get_cached_hud_image(icon_path)
            if not img_btn.isNull():
                painter.drawImage(QPoint(x_offset, y_pos), img_btn)
                x_offset += 50
                
        painter.end()
        
        # --- NEW: Route the painted frame to PiP or Main Label ---
        if self.pip_window and self.pip_window.isVisible():
            # Send the painted frame to the floating window
            self.pip_window.update_image(pixmap)
        else:
            # Send the painted frame to the main UI
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
            # Conectamos la señal que creamos para detectar la 'X'
            self.pip_window.window_closed.connect(self._on_pip_closed_externally)
            self.pip_window.show()
            self.ui.videoLabel.setText("PiP Mode Active. Look at floating window.")
            self.ui.pipButton.setText("Return to Main UI")
            return True
        else:
            # Al cerrar por código, también se disparará window_closed automáticamente
            self.pip_window.close()
            return False

    def _on_pip_closed_externally(self):
        """Restaura la interfaz cuando la ventana PiP se cierra por cualquier motivo."""
        # 1. Comprobamos si la ventana principal está minimizada
        if self.isMinimized():
            self.showNormal()      # La desminimizamos al estado en el que estaba
            self.activateWindow()  # La traemos al frente y le damos el foco del sistema
            
        # 2. Limpiamos la referencia y restauramos los textos del botón
        self.pip_window = None
        self.ui.pipButton.setText("PiP Mode")

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


    def populate_profiles(self, profiles_list):
        """Genera QToolButtons dinámicos (Composición Vertical: Icono sobre Texto)"""
        # 1. Limpiar el grid actual por completo
        while self.ui.layoutProfiles.count():
            item = self.ui.layoutProfiles.takeAt(0)
            widget = item.widget()
            if widget:
                self.profile_button_group.removeButton(widget)
                widget.deleteLater()
                
        # Si no hay perfiles, no hacemos nada más
        if not profiles_list:
            return
            
        # 2. Calcular columnas ideales para la forma cuadrada
        import math
        columnas_ideales = math.ceil(math.sqrt(len(profiles_list)))
                
        # 3. Generar los nuevos QToolButtons
        row, col = 0, 0
        
        # Obtenemos la ruta absoluta al icono que el usuario puso en la raíz
        from model import get_asset_path
        icon_path = get_asset_path('file_icon.png') # <-- Asegúrate de que existe este archivo
        file_icon = QIcon(icon_path)

        for profile in profiles_list:
            clean_name = profile.replace('.json', '')
            
            # --- CREACIÓN DEL COMPONENTE TIPO DIBUJO ---
            btn = QToolButton()
            btn.setText(clean_name.upper()) # Texto limpio en mayúsculas
            btn.setIcon(file_icon)          # El icono PNG real
            btn.setIconSize(QSize(64, 64))  # Icono grande (ajusta si lo prefieres mayor)
            
            # ESTILO CLAVE: Icono arriba, texto abajo
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Comportamiento: Es un botón de radio
            btn.setCheckable(True)
            btn.setProperty("filename", profile)
            
            # Política de tamaño: Que ocupe todo el ancho y alto disponible en su celda del grid
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumHeight(150) # Altura mínima para que quepa bien verticalmente
            btn.setFocusPolicy(Qt.StrongFocus)
            self.profile_button_group.addButton(btn)
            # Inyectamos en el layout
            self.ui.layoutProfiles.addWidget(btn, row, col)
            
            # Lógica dinámica cuadrada
            col += 1
            if col >= columnas_ideales: 
                col = 0
                row += 1

    def _on_accept_profile(self):
        """Envía el nombre del archivo seleccionado al presentador."""
        checked_btn = self.profile_button_group.checkedButton()
        if checked_btn:
            self.profile_accepted.emit(checked_btn.property("filename"))

    def build_virtual_keyboard(self):
        """Construye un teclado dinámico simétrico de 13 columnas por fila."""
        from PySide6.QtWidgets import QPushButton, QSizePolicy

        self.is_caps = False   # CORRECCIÓN: El teclado ahora nace en minúsculas
        self.is_shift = False 
        self.keyboard_buttons = [] 

        # Distribución perfectamente equilibrada (13 elementos por fila)
        teclas = [
            ['º', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '?', '¡'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '`', '+'],
            ['BLOQ', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Ñ', '´', 'Ç'],
            ['SHIFT', '<', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '-', 'SHIFT'],
            ['ESPACIO']
        ]
        
        for row_idx, fila in enumerate(teclas):
            for col_idx, tecla in enumerate(fila):
                btn = QPushButton()
                btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                btn.setMinimumHeight(60)
                
                if tecla == 'ESPACIO':
                    self.ui.keyboardGridLayout.addWidget(btn, row_idx, 0, 1, 13)
                else:
                    self.ui.keyboardGridLayout.addWidget(btn, row_idx, col_idx)

                btn.clicked.connect(lambda checked=False, char=tecla: self._on_key_pressed(char))
                self.keyboard_buttons.append({'btn': btn, 'base': tecla})

        self._update_keyboard_labels()

    def _update_keyboard_labels(self):
        """Repinta las etiquetas de la matriz según el estado de BLOQ MAYÚS y SHIFT."""
        # Añadido el mapa de caracteres para la nueva tecla 'º' -> 'ª'
        shift_map = {
            'º': 'ª', '1': '!', '2': '"', '3': '·', '4': '$', '5': '%', '6': '&&', '7': '/',
            '8': '(', '9': ')', '0': '=', '?': "'", '¡': '¿',
            '`': '^', '+': '*', '´': '¨', '<': '>', ',': ';', '.': ':', '-': '_'
        }

        for item in self.keyboard_buttons:
            btn = item['btn']
            base = item['base']

            # Teclas de control (No se alteran con shift/mayúsculas textualmente)
            if base in ['BLOQ', 'SHIFT', 'ESPACIO', 'TAB']:
                btn.setText(base)
                # Iluminación de estado para ambos botones SHIFT y el BLOQ
                if base == 'BLOQ':
                    btn.setStyleSheet("background-color: #0078D7; border-color: #ffffff;" if self.is_caps else "")
                elif base == 'SHIFT':
                    btn.setStyleSheet("background-color: #0078D7; border-color: #ffffff;" if self.is_shift else "")
            
            # Letras básicas
            elif base.isalpha() and len(base) == 1 and base != 'º':
                if self.is_caps ^ self.is_shift: 
                    btn.setText(base.upper())
                else:
                    btn.setText(base.lower())
            
            # Números y símbolos especiales
            else:
                if self.is_shift:
                    btn.setText(shift_map.get(base, base))
                else:
                    btn.setText(base)
                
            

    def _on_key_pressed(self, char):
        """Procesa la inserción de texto o los cambios de estado del teclado."""
        current_text = self.ui.keyboardDisplay.text()
        
        if char == 'BLOQ':
            self.is_caps = not self.is_caps
            self._update_keyboard_labels()
            return
            
        elif char == 'SHIFT':
            self.is_shift = not self.is_shift
            self._update_keyboard_labels()
            return
            
        elif char == 'ESPACIO':
            if len(current_text) < 30:
                self.ui.keyboardDisplay.setText(current_text + " ")
                
        elif char == 'TAB':
            if len(current_text) < 30:
                # El tabulador inserta un bloque de 4 espacios para mantener un espaciado limpio
                self.ui.keyboardDisplay.setText(current_text + "    ")
                
        else:
            if len(current_text) < 30:
                # Recupera de forma segura el texto pintado en el botón pulsado actualmente
                for item in self.keyboard_buttons:
                    if item['base'] == char:
                        char_to_write = item['btn'].text()
                        if(char_to_write == '&&'):
                            char_to_write = '&'  # Corrección para mostrar '&' en el display en lugar de '&&'
                        self.ui.keyboardDisplay.setText(current_text + char_to_write)
                        break

        # Desactivar el shift tras una pulsación ordinaria de escritura
        if self.is_shift and char not in ['BLOQ', 'SHIFT', 'TAB']:
            self.is_shift = False
            self._update_keyboard_labels()

    def open_virtual_keyboard(self):
        """Limpia la pantalla del teclado y resetea los modificadores al entrar."""
        self.ui.keyboardDisplay.setText("")
        self.is_shift = False
        self.is_caps = False # CORRECCIÓN: Minúsculas por defecto al abrir la pantalla de escritura
        self._update_keyboard_labels()
        self.show_page(4)

   

    def _on_keyboard_backspace(self):
        """Borra la última letra."""
        texto_actual = self.ui.keyboardDisplay.text()
        self.ui.keyboardDisplay.setText(texto_actual[:-1])

    def _on_keyboard_accept(self):
        """Envía el texto al presentador si no está vacío."""
        filename = self.ui.keyboardDisplay.text().strip()
        if filename:
            self.save_as_requested.emit(filename)


    def populate_explorer(self, current_path, items_list, mode="FOLDER",page_index_return=None):
        """Generates interactive buttons for folders and optionally .exe files."""
        self.ui.label_explorer_path.setText(f"Ruta actual: {current_path}")
        
        while self.ui.layoutExplorer.count():
            item = self.ui.layoutExplorer.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Adapt UI based on the active mode
        if mode == "FOLDER":
            self.ui.explorerSelectButton.setText("✅ ELEGIR ESTA CARPETA")
        elif mode == "EMULATOR":
            self.ui.explorerSelectButton.setText("🖥️ PREDETERMINADO WINDOWS")

        ideal_columns = 5 
        row, col = 0, 0
        
        # items_list now receives tuples: (filename, type)
        for item_name, item_type in items_list:
            btn = QToolButton()
            multiline_text = textwrap.fill(item_name, width=12)
            btn.setText(multiline_text)
            
            btn.setIconSize(QSize(60, 60))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setFocusPolicy(Qt.StrongFocus)
            
            # Emit different signals based on the file type
            if item_type == "folder":
                btn.clicked.connect(lambda checked=False, f=item_name: self.explorer_folder_clicked.emit(f))
            elif item_type == "exe":
                btn.clicked.connect(lambda checked=False, f=item_name: self.emulator_exe_chosen.emit(f, page_index_return))
            
            self.ui.layoutExplorer.addWidget(btn, row, col)
            
            col += 1
            if col >= ideal_columns:
                col = 0
                row += 1


    def populate_emulator_settings(self, emulators_dict):
        """Dynamically generates the emulator configuration rows."""
        layout = self.ui.layoutDynamicEmulators
        
        # --- NUEVA LIMPIEZA PROFUNDA (Deep Clear) ---
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget: 
                widget.deleteLater()
            elif item.layout():
                # Si es una fila (QHBoxLayout), entramos a borrar sus botones y textos
                sub_layout = item.layout()
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    sub_widget = sub_item.widget()
                    if sub_widget:
                        sub_widget.deleteLater()
                sub_layout.deleteLater() # Borramos la fila vacía
            elif item.spacerItem(): 
                layout.removeItem(item)

        from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QFont
        import os

        # Title
        title_lbl = QLabel("CONFIGURACIÓN DE EMULADORES")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_lbl.setFont(title_font)
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        # Dynamic rows
        for console, current_emu in emulators_dict.items():
            row_layout = QHBoxLayout()
            
            console_lbl = QLabel(console)
            console_lbl.setMinimumWidth(150)
            font_lbl = QFont()
            font_lbl.setPointSize(12)
            console_lbl.setFont(font_lbl)
            
            btn = QPushButton()
            btn.setMinimumHeight(50)
            
            # Show only the executable name if a full path is set
            if current_emu != "Default" and os.path.exists(current_emu):
                display_text = os.path.basename(current_emu)
            else:
                display_text = current_emu
                
            btn.setText(display_text)
            btn.clicked.connect(lambda checked=False, c=console: self.emulator_setup_requested.emit(c,6))
            
            row_layout.addWidget(console_lbl)
            row_layout.addWidget(btn)
            layout.addLayout(row_layout)
            
        
        layout.addStretch()


    def populate_platforms_catalog(self, platforms_list):
        """Dibuja un QToolButton por cada plataforma en el layout de la nueva pantalla."""
        
        # 1. Limpiar el contenedor por si había botones viejos
        while self.ui.layoutPlatforms.count():
            item = self.ui.layoutPlatforms.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # --- NUEVA LÓGICA DE CUADRÍCULA ---
        max_columnas = 4 # Cámbialo al número de tarjetas que quieras por fila
        fila = 0
        columna = 0

        # 2. Crear los botones
        for platform_name in platforms_list:
            btn = QToolButton()
            btn.setText(platform_name)
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            
            # Opcional: Asignar icono
            # if platform_name == "Steam": btn.setIcon(QIcon("rutas/steam.png"))
            
            # Conexión del botón
            btn.clicked.connect(lambda checked=False, p=platform_name: self.platform_selected.emit(p))
            
            # 3. Añadir el botón indicando sus coordenadas exactas (Fila, Columna)
            self.ui.layoutPlatforms.addWidget(btn, fila, columna)
            
            # 4. Calcular el hueco para el siguiente botón
            columna += 1
            if columna >= max_columnas:
                columna = 0  # Volvemos a la izquierda del todo
                fila += 1    # Bajamos un piso


    def populate_games_catalog(self, games_list, platform_name, emulator_name=None):
        """Genera botones solo para los juegos recibidos y actualiza el título."""
        
        # --- NUEVO: Actualizar el label superior ---
        # (Asegúrate de que el label se llama 'platformLabel' en tu Qt Designer)
        self.ui.platformLabel.setText(f"Plataforma: {platform_name}")
        
        if(platform_name=="Steam"):
            self.ui.gamesEmulatorsButton.hide()  # Oculta el botón de emuladores para Steam
        else:
            if(emulator_name!=None):
                self.ui.gamesEmulatorsButton.show()  # Asegura que el botón esté visible para otras plataformas
                self.ui.gamesEmulatorsButton.setText(f"Emulador:\n{os.path.splitext(os.path.basename(emulator_name))[0].upper()}")
                try:
                    # Limpiamos cualquier conexión previa (evita que se acumulen plataformas antiguas)
                    self.ui.gamesEmulatorsButton.clicked.disconnect()
                except (RuntimeError, TypeError):
                    # Si el botón no tenía conexiones previas, ignoramos el aviso de Qt de forma segura
                    pass
                
                # Conectamos la señal absorbiendo el booleano 'checked' de Qt y congelando 'platform_name'
                self.ui.gamesEmulatorsButton.clicked.connect(
                    lambda checked=False: self.emulator_setup_requested.emit(platform_name,5)
                )

        while self.ui.layoutGames.count():
            item = self.ui.layoutGames.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not games_list:
            return


        columnas_ideales = math.ceil(math.sqrt(len(games_list)))
        icono_defecto = QIcon(get_asset_path('game_default.png')) 

        row, col = 0, 0

        for juego in games_list:
            titulo_crudo = juego.get("title", "JUEGO DESCONOCIDO").upper()
            exe_path = juego.get("exe_path", "") 
            
            titulo_multilinea = textwrap.fill(titulo_crudo, width=12)
            
            btn = QToolButton()
            btn.setText(titulo_multilinea)
            
            ruta_icono = juego.get("icon")
            btn.setIcon(QIcon(get_asset_path(ruta_icono)) if ruta_icono else icono_defecto)
            btn.setIconSize(QSize(100,80))
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setFocusPolicy(Qt.StrongFocus)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            
            btn.clicked.connect(lambda checked=False, path=exe_path: self.game_launch_requested.emit(path))
            
            self.ui.layoutGames.addWidget(btn, row, col)
            
            col += 1
            if col >= columnas_ideales:
                col = 0
                row += 1

    def show_controller_image(self, image_path):
        """Carga la imagen, la muestra, y espera a que el layout se calcule."""
        from PySide6.QtGui import QPixmap
        from PySide6.QtCore import QTimer
        from model import get_asset_path
        
        self.current_controller_path = image_path
        ruta_absoluta = get_asset_path(image_path)
        
        # 1. Guardamos la foto original en la RAM para no castigar al disco duro al redimensionar
        self._pixmap_original = QPixmap(ruta_absoluta)
        
        if not self._pixmap_original.isNull():
            # 2. Apagamos el tirano y mostramos el widget para que el Layout actúe
            self.ui.controllerImage.setScaledContents(False)
            self.ui.controllerImage.show()
            
            # 3. LA MAGIA: Ponemos el escalado a la cola. Se ejecutará en cuanto 
            # el Layout termine de calcular el ancho real de la columna.
            QTimer.singleShot(0, self._apply_controller_scaling)

    def _apply_controller_scaling(self):
        """Aplica la matemática del escalado usando el ancho 100% real."""
        from PySide6.QtCore import Qt
        
        # Nos aseguramos de que la imagen original se cargó bien
        if hasattr(self, '_pixmap_original') and not self._pixmap_original.isNull():
            # Ahora sí, este width() es matemáticamente perfecto
            ancho_real = self.ui.controllerImage.width()
            
            pixmap_escalado = self._pixmap_original.scaledToWidth(ancho_real, Qt.SmoothTransformation)
            
            self.ui.controllerImage.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.ui.controllerImage.setPixmap(pixmap_escalado)

    def hide_controller_image(self):
        """Oculta la imagen de la interfaz."""
        self.ui.controllerImage.hide()

    def resizeEvent(self, event):
        """Recalcula el tamaño de la imagen si el usuario estira la ventana."""
        super().resizeEvent(event) 
        
        # Si la imagen está visible, llamamos a la función matemática directamente,
        # aprovechando que la imagen original ya está guardada en self._pixmap_original
        if hasattr(self, 'ui') and self.ui.controllerImage.isVisible() and self.current_controller_path:
            self._apply_controller_scaling()

    def _get_cached_hud_image(self, relative_path):
        """Retrieves an image from RAM or loads and pre-scales it if not cached."""
        if relative_path not in self.hud_image_cache:
            full_path = get_asset_path(relative_path)
            img = QImage(full_path)
            
            if not img.isNull():
                # Cache the image ALREADY SCALED to save CPU cycles during the video loop
                self.hud_image_cache[relative_path] = img.scaled(
                    40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            else:
                # Cache an empty image to prevent spamming disk reads if a file is missing
                self.hud_image_cache[relative_path] = QImage()
                
        return self.hud_image_cache[relative_path]
    
    def update_navigation_sliders(self, val_x, val_y):
        """Actualiza la barra azul de los sliders de calibración en tiempo real."""
        if hasattr(self.ui, 'slider_x') and hasattr(self.ui, 'slider_y'):
            self.ui.slider_x.set_current_value(val_x)
            self.ui.slider_y.set_current_value(val_y)


    def set_navigation_thumbs(self, low_x, high_x, low_y, high_y):
        """Posiciona los thumbs iniciales al abrir la pantalla."""
        if hasattr(self.ui, 'slider_x') and hasattr(self.ui, 'slider_y'):
            self.ui.slider_x.low_thumb = low_x
            self.ui.slider_x.high_thumb = high_x
            self.ui.slider_x.update()
            
            self.ui.slider_y.low_thumb = low_y
            self.ui.slider_y.high_thumb = high_y
            self.ui.slider_y.update()

    def changeEvent(self, event):
        """Detecta cambios en el estado de la ventana (minimizar, restaurar, maximizar)."""
        # 1. Comprobamos si el evento es un cambio en el estado de la ventana
        if event.type() == QEvent.WindowStateChange:
            
            # 2. Comprobamos si la ventana YA NO está minimizada (es decir, acaba de restaurarse)
            if not (self.windowState() & Qt.WindowMinimized):
                
                # 3. Si la ventana PiP flotante está viva (separada), la destruimos
                if getattr(self, 'pip_window', None) is not None:
                    self.pip_window.close() 
                    # Nota: Al hacer .close(), saltará automáticamente tu método 
                    # _on_pip_closed_externally, el cual se encargará de reubicar
                    # el vídeo en la interfaz principal y resetear los botones.
                    
        # Siempre debemos llamar al método original al final para no romper Qt
        super().changeEvent(event)