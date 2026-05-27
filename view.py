from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton, QButtonGroup, QToolButton, QSizePolicy
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, Qt, QSize
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
    gesture_selected = Signal(object)      # Sends the gesture button object
    stop_reading_score = Signal()
    save_controls = Signal(str, str, int)  # gesture_code, input_code, threshold
    save_mapping_current = Signal()  # Signal to save the mapping on already loaded file
    load_profiles_requested = Signal()
    profile_accepted = Signal(str)
    save_as_requested = Signal(str) # Envía el nombre del nuevo archivo

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
        from model import resolve_path
        icon_path = resolve_path('file_icon.png') # <-- Asegúrate de que existe este archivo
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