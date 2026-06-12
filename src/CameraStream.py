"""
MÓDULO CameraStream.py
---------------------------------------------------------
Implementa la captura de vídeo en un hilo (thread) independiente.
Evita que el cuello de botella de lectura del hardware de la cámara (I/O) 
congele o ralentice el procesamiento de la Inteligencia Artificial y la UI.
"""

import threading
import cv2

class CameraStream:
    """
    Clase encargada de mantener un flujo constante de frames desde la cámara web
    hacia la memoria RAM utilizando concurrencia (threading).
    """
    def __init__(self, src=0, target_fps=60):
        # 1. En Windows, CAP_DSHOW (DirectShow) acelera drásticamente el tiempo de inicio de la cámara
        # y estabiliza el framerate en comparación con el backend por defecto.
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        
        # 2. Forzamos el codec MJPG. Es vital para que las webcams por USB puedan superar 
        # el límite nativo de 30 FPS y alcanzar los 60 FPS deseados.
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # 3. Pedimos una resolución estándar de 640x480.
        # Bajar la resolución de captura reduce la carga en el bus USB y aumenta los FPS disponibles.
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 4. Solicitamos físicamente a la lente de la cámara que opere a los FPS objetivo.
        self.cap.set(cv2.CAP_PROP_FPS, target_fps)
        
        # Leemos el primer frame para inicializar las variables
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        
        # Un 'Lock' (Candado) evita problemas de condición de carrera si la IA
        # intenta leer un frame justo en el mismo milisegundo que la cámara lo está sobreescribiendo.
        self.lock = threading.Lock()

    def start(self):
        """Arranca el hilo secundario para comenzar a actualizar los frames en segundo plano."""
        t = threading.Thread(target=self.update, args=())
        t.daemon = True  # Al ser un hilo 'daemon', morirá automáticamente cuando se cierre el programa principal
        t.start()
        return self

    def update(self):
        """Bucle infinito del hilo secundario que lee constantemente la cámara."""
        while not self.stopped:
            ret, frame = self.cap.read()
            # Adquirimos el candado solo durante la micro-fracción de segundo que toma actualizar la variable
            with self.lock:
                self.ret = ret
                self.frame = frame
                
        # CRÍTICO: Una vez que el bucle se detiene, liberamos el hardware de la cámara físicamente
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

    def read(self):
        """Devuelve una copia segura del frame más reciente capturado."""
        with self.lock:
            # Usamos .copy() para que el consumidor (IA) manipule la imagen sin afectar el original
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """Señaliza al bucle secundario que debe detenerse y liberar los recursos."""
        self.stopped = True