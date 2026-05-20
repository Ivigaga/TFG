import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtUiTools import QUiLoader

# Importamos la clase lógica del otro archivo
from CameraController import GestosControlador

# --- VENTANA FLOTANTE PiP ---
class VentanaVideoFlotante(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video PiP")
        self.resize(320, 240)
        
        # Esto hace que la ventana se quede siempre por encima
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        
        # Quitamos márgenes para que sea puro video
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setStyleSheet("background-color: black;")
        layout.addWidget(self.label_video)

    def actualizar_imagen(self, pixmap):
        self.label_video.setPixmap(pixmap.scaled(
            self.label_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))

# --- INTERFAZ PRINCIPAL ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Cargar la UI
        loader = QUiLoader()
        # ASEGÚRATE DE QUE TU ARCHIVO XML SE LLAME ASÍ:
        self.ui = loader.load("prueba.ui", None) 
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Control Gestual - PySide6")
        self.resize(1020, 751)

        # Variables de control PiP
        self.ventana_flotante = None
        
        self.assignButtons()

        # 1. Iniciamos la lógica de la cámara y Mediapipe
        self.controlador = GestosControlador()

        # 2. Configurar el evento de reloj (QTimer) a ~60 FPS
        self.timer_video = QTimer(self)
        self.timer_video.timeout.connect(self.capturar_y_enrutar)
        self.startVideo()

    def capturar_y_enrutar(self):
        # Pedimos un frame a la lógica
        frame = self.controlador.procesar_frame_unico()
        if frame is None: 
            return

        # Convertimos la imagen de OpenCV (BGR) a formato Qt (RGB)
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = color_frame.shape
        qt_imagen = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_imagen)

        # Decidimos a qué ventana enviar la imagen
        if self.ventana_flotante and self.ventana_flotante.isVisible():
            # Si el PiP está activo, pintamos allí
            self.ventana_flotante.actualizar_imagen(pixmap)
        else:
            # Control de seguridad si el usuario cerró el PiP manualmente con la 'X'
            if self.ventana_flotante:
                self.ventana_flotante = None
                self.ui.pipButton.setText("Modo PiP")
                
            # Si no hay PiP, pintamos en la ventana principal
            self.ui.videoLabel.setPixmap(pixmap.scaled(
                self.ui.videoLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def assignButtons(self):
        self.ui.pipButton.clicked.connect(self.toggle_pip)
        self.ui.stopButton.clicked.connect(self.controlVideo)
        self.ui.changeControlsButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.controlsCancelButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.gesturesBackButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.A_button.clicked.connect(lambda: self.showChangeControls(self.ui.A_button))
        self.ui.B_button.clicked.connect(lambda: self.showChangeControls(self.ui.B_button))
        self.ui.Select_button.clicked.connect(lambda: self.showChangeControls(self.ui.Select_button))
        self.ui.Start_button.clicked.connect(lambda: self.showChangeControls(self.ui.Start_button))

    def toggle_pip(self):
        if not self.ventana_flotante:
            # Activar ventana PiP
            self.ventana_flotante = VentanaVideoFlotante()
            self.ventana_flotante.show()
            self.ui.videoLabel.setText("Modo PiP activo. Mira la ventana flotante.")
            self.ui.pipButton.setText("Volver a UI Principal")
        else:
            # Desactivar ventana PiP
            self.ventana_flotante.close()
            self.ventana_flotante = None
            self.ui.pipButton.setText("Modo PiP")

    def closeEvent(self, event):
        # Detener la cámara y el reloj limpiamente al cerrar la App
        self.timer_video.stop()
        self.controlador.cerrar_recursos()
        if self.ventana_flotante:
            self.ventana_flotante.close()
        event.accept()

    def controlVideo(self):
        if self.timer_video.isActive():
            self.stopVideo()
        else:
            self.startVideo()

    def startVideo(self):
        self.timer_video.start(16) # Reiniciar el timer si es necesario
        self.ui.pipButton.setEnabled(True)
        self.ui.stopButton.setText("Pausar video")
    
    def stopVideo(self):
        self.timer_video.stop() # Detener el timer si es necesario
        self.ui.pipButton.setEnabled(False)
        self.ui.videoLabel.setText("Video pausado.")
        self.ui.stopButton.setText("Reanudar video")
        if self.ventana_flotante:
            # Desactivar ventana PiP
            self.ventana_flotante.close()
            self.ventana_flotante = None
            self.ui.pipButton.setText("Modo PiP")

    def showChangeControls(self,button):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.buttonLabel.setProperty("button", button.property("gamepadInput"))
        self.ui.buttonLabel.setText(button.text())
        gestureButton = self.getGestureButtonForInput(button.property("gamepadInput"))
        if gestureButton:
            gestureButton.setChecked(True)

    def getGestureButtonForInput(self, button):
        gesture=self.controlador.getGestureForButton(button)
        if gesture:
            gesture_buttons = self.ui.buttonGroup.buttons()
            # Recorres la lista con un bucle for
            for button in gesture_buttons:
                if button.property("gesture") == gesture:
                    return button
        return None


            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())