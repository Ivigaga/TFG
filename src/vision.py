"""
MÓDULO vision.py
---------------------------------------------------------
Contiene el Motor de Visión, encargado de procesar la Inteligencia Artificial (MediaPipe).
Al heredar de QThread, este código se ejecuta en un núcleo paralelo del procesador,
asegurando que la interfaz de la aplicación nunca se congele.
"""

import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QThread, Signal
from CameraStream import CameraStream

class VisionEngine(QThread):
    """
    Motor asíncrono para captura facial. 
    Interconecta el hilo secundario de la cámara (Hardware) con el hilo 
    secundario de la IA y escupe los resultados al hilo principal de la UI.
    """
    
    # Definimos la señal que escupirá los datos al Presentador en el formato:
    # (frame_imagen, diccionario_blendshapes, coordenadas_puntos_faciales, es_nuevo_dato_IA)
    frame_processed = Signal(object, object, object, bool)

    def __init__(self, model_path, target_fps=60):
        super().__init__() # Obligatorio al heredar de QThread
        self.target_fps = target_fps
        self.last_inference_time = 0
        self.timestamp_ms = 0
        self.is_running = True
        
        self.current_result = None
        self.cam = self._initialize_camera()
        self.detector = self._initialize_detector(model_path)

    def _initialize_camera(self):
        """
        Escanea los puertos USB en busca de una cámara disponible y la arranca.
        
        Raises:
            Exception: Si falla al leer los puertos tras 5 intentos.
        """
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Encontramos cámara válida. Liberamos OpenCV básico y arrancamos
                    # nuestro hilo optimizado CameraStream
                    cap.release()
                    return CameraStream(src=index, target_fps=self.target_fps).start()
            cap.release()
            
        raise Exception("CRITICAL ERROR: No camera detected.")

    def _result_callback(self, result, output_image, timestamp_ms):
        """
        Función 'Callback' invocada asíncronamente por MediaPipe desde C++ 
        cuando termina de procesar un fotograma de red neuronal.
        """
        self.current_result = result

    def _initialize_detector(self, model_path):
        """Carga y configura el modelo de Machine Learning (FaceLandmarker)."""
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM, # Modo vídeo continuo para baja latencia
            result_callback=self._result_callback,
            output_face_blendshapes=True, # Requerimos la extracción de gestos expresivos (score 0-1)
            num_faces=1                   # Limitado a 1 cara para ahorrar recursos
        )
        return vision.FaceLandmarker.create_from_options(options)

    # El método run() es el corazón del QThread. Todo lo que esté aquí dentro 
    # se procesa fuera del hilo principal de la aplicación.
    def run(self):
        while self.is_running:
            loop_start = time.perf_counter() # 1. Marcamos cronómetro: inicio del frame
            
            # Obtenemos el último frame del hilo optimizado de cámara
            frame = self.cam.read()
            if frame is None:
                time.sleep(0.01) # Si la cámara falla/tarda, dormimos 10ms para no quemar la CPU
                continue

            is_new_processing = False
            current_now = time.perf_counter()
            
            # --- CONTROL DE FPS DE LA INTELIGENCIA ARTIFICIAL ---
            # Aunque la cámara vaya a 100 FPS, limitamos la carga matemática a los target_fps (60)
            if (current_now - self.last_inference_time) >= (1 / self.target_fps):
                # Convertimos BGR (OpenCV) a RGB (MediaPipe)
                rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_small)
                
                # Inyección asíncrona a la red neuronal
                self.timestamp_ms += int(1000 / self.target_fps)
                self.detector.detect_async(mp_image, self.timestamp_ms)
                
                self.last_inference_time = current_now
                is_new_processing = True

            # Efecto espejo (es más intuitivo para el usuario moverse viéndose al revés)
            frame = cv2.flip(frame, 1)
            
            blendshapes = None
            landmarks = None
            
            # Extraer resultados devueltos por el Callback
            if self.current_result:
                if self.current_result.face_blendshapes:
                    # Convertimos la estructura compleja a un diccionario plano simple {"smile": 0.8}
                    blendshapes = {cat.category_name: cat.score for cat in self.current_result.face_blendshapes[0]}
                if self.current_result.face_landmarks:
                    landmarks = self.current_result.face_landmarks[0]

            # Emitimos el "Paquete" de vuelta al Hilo Principal (al Presentador)
            self.frame_processed.emit(frame, blendshapes, landmarks, is_new_processing)
            
            # --- EL ACELERADOR Y FRENO (THROTTLING) ---
            # Calculamos cuánto tiempo sobró de este frame.
            # Dormimos el hilo exactamente los milisegundos restantes para asegurar 60 FPS estables.
            elapsed_time = time.perf_counter() - loop_start
            time_left_to_sleep = (1.0 / self.target_fps) - elapsed_time
            
            if time_left_to_sleep > 0:
                time.sleep(time_left_to_sleep)

    def release_resources(self):
        """
        Ejecuta un apagado ordenado y seguro previniendo fugas de memoria 
        (Memory Leaks) al cerrar la aplicación.
        """
        self.is_running = False
        
        # 1. Avisamos a la cámara que pare ANTES de bloquear este hilo
        if hasattr(self, 'cam') and self.cam:
            self.cam.stop()
            time.sleep(0.2)  # Dar tiempo a que el bucle interno del Stream se cierre
            
        # 2. Esperamos limpiamente a que este QThread termine su bucle run()
        self.wait(2000)  # Esperar un máximo de 2 segundos (timeout)
        
        # 3. Forzar quit() brusco si aún sigue atascado
        if self.isRunning():
            self.quit()
            self.wait(1000)
        
        # 4. CRÍTICO: Apagar el motor de MediaPipe (Libera objetos y memoria asignados en C++)
        if hasattr(self, 'detector') and self.detector:
            self.detector.close()