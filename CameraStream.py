import threading
import cv2
class CameraStream:
    def __init__(self, src=0, target_fps=60):
        # 1. En Windows, CAP_DSHOW acelera drásticamente el inicio y el framerate
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        
        # 2. Forzamos el codec MJPG (vital para que las webcams USB pasen de 30 FPS)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        # 3. Pedimos resolución estándar (bajar la resolución aumenta los FPS libres de hardware)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # 4. Solicitamos físicamente los 60 FPS a la lente
        self.cap.set(cv2.CAP_PROP_FPS, target_fps)
        
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        t = threading.Thread(target=self.update, args=())
        t.daemon = True  # Muere con el programa principal
        t.start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret = ret
                self.frame = frame
                
        # CRÍTICO: Liberar la cámara físicamente al salir del bucle
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.stopped = True