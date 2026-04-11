import sys
import cv2
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtUiTools import QUiLoader

# Importamos la clase que hemos creado en tu archivo original
from CameraController import GestosControlador

class HiloVideo(QThread):
    # Esta señal enviará la imagen procesada de vuelta a la interfaz
    senal_actualizar_imagen = Signal(QImage)

    def __init__(self):
        super().__init__()
        self._corriendo = True
        self.controlador = GestosControlador()

    def run(self):
        # Este es el equivalente a tu antiguo 'while True'
        while self._corriendo:
            frame = self.controlador.procesar_frame_unico()
            
            if frame is not None:
                # Convertimos la imagen de OpenCV (BGR) a formato Qt (RGB)
                color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = color_frame.shape
                bytes_por_linea = ch * w
                
                # Creamos el objeto QImage
                qt_imagen = QImage(color_frame.data, w, h, bytes_por_linea, QImage.Format_RGB888)
                
                # Emitimos la imagen para que la interfaz la reciba
                self.senal_actualizar_imagen.emit(qt_imagen)

    def detener(self):
        self._corriendo = False
        self.controlador.cerrar_recursos()
        self.wait() # Esperamos a que el hilo termine de forma segura

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loader = QUiLoader()
        self.ui = loader.load("prueba.ui", None) 
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Control Gestual - PySide6")
        self.resize(1020, 751)

        # Variable para controlar si la ventana PiP está abierta
        self.ventana_flotante = None

        # Configurar uno de tus botones para el modo PiP (asumo que usas 'pushButton')
        self.ui.pushButton.setText("Modo PiP")
        self.ui.pushButton.clicked.connect(self.toggle_pip)

        # Configuramos el hilo de video
        self.hilo_video = HiloVideo()
        self.hilo_video.senal_actualizar_imagen.connect(self.enrutar_video)
        self.hilo_video.start()

    def toggle_pip(self):
        if self.ventana_flotante is None:
            # ACTIVAR PiP
            self.ventana_flotante = VentanaVideoFlotante()
            self.ventana_flotante.show()
            self.ui.videoLabel.setText("Video reproduciéndose en ventana flotante...")
            self.ui.pushButton.setText("Volver a UI Principal")
        else:
            # DESACTIVAR PiP
            self.ventana_flotante.close()
            self.ventana_flotante = None
            self.ui.pushButton.setText("Modo PiP")

    def enrutar_video(self, qt_imagen):
        # Convertimos la imagen base a Pixmap una sola vez
        pixmap = QPixmap.fromImage(qt_imagen)

        # Si la ventana flotante existe y está visible, le mandamos el video a ella
        if self.ventana_flotante is not None and self.ventana_flotante.isVisible():
            self.ventana_flotante.actualizar_imagen(pixmap)
        else:
            # Control de seguridad: por si el usuario cerró el PiP desde la 'X' de la ventana
            if self.ventana_flotante is not None:
                self.ventana_flotante = None
                self.ui.pushButton.setText("Modo PiP")

            # Si no hay PiP, dibujamos en la ventana principal
            pixmap_escalado = pixmap.scaled(
                self.ui.videoLabel.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.ui.videoLabel.setPixmap(pixmap_escalado)

    def closeEvent(self, event):
        # Detenemos el hilo, limpiamos la cámara y cerramos el PiP si está abierto
        self.hilo_video.detener()
        if self.ventana_flotante is not None:
            self.ventana_flotante.close()
        event.accept()

class VentanaVideoFlotante(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video PiP")
        self.resize(320, 240)
        
        # MAGIA AQUÍ: Le decimos que sea una ventana de herramienta y se quede siempre arriba
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        
        # Layout sin márgenes para que el video ocupe todo
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_video = QLabel(self)
        self.label_video.setAlignment(Qt.AlignCenter)
        self.label_video.setStyleSheet("background-color: black;")
        layout.addWidget(self.label_video)

    def actualizar_imagen(self, pixmap):
        # Actualiza el tamaño dinámicamente si el usuario redimensiona la mini-ventana
        self.label_video.setPixmap(pixmap.scaled(
            self.label_video.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec())