import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PySide6.QtCore import QThread, Signal
from CameraStream import CameraStream

class VisionEngine(QThread):
    # Definimos la señal que escupirá los datos: frame, blendshapes, landmarks, is_new_processing
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
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return CameraStream(src=index, target_fps=self.target_fps).start()
            cap.release()
        raise Exception("CRITICAL ERROR: No camera detected.")

    def _result_callback(self, result, output_image, timestamp_ms):
        self.current_result = result

    def _initialize_detector(self, model_path):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
            output_face_blendshapes=True,
            num_faces=1
        )
        return vision.FaceLandmarker.create_from_options(options)

    # El método run() es el corazón del QThread. Se ejecuta en un núcleo paralelo.
    def run(self):
        while self.is_running:
            loop_start = time.perf_counter() # 1. Marcamos cuándo empieza el frame
            
            frame = self.cam.read()
            if frame is None:
                time.sleep(0.01) # 2. Aumentamos el descanso a 10ms si no hay cámara
                continue

            is_new_processing = False
            current_now = time.perf_counter()
            
            # Control de FPS de la IA
            if (current_now - self.last_inference_time) >= (1 / self.target_fps):
                rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_small)
                
                self.timestamp_ms += int(1000 / self.target_fps)
                self.detector.detect_async(mp_image, self.timestamp_ms)
                self.last_inference_time = current_now
                is_new_processing = True

            frame = cv2.flip(frame, 1)
            
            blendshapes = None
            landmarks = None
            
            if self.current_result:
                if self.current_result.face_blendshapes:
                    blendshapes = {cat.category_name: cat.score for cat in self.current_result.face_blendshapes[0]}
                if self.current_result.face_landmarks:
                    landmarks = self.current_result.face_landmarks[0]

            self.frame_processed.emit(frame, blendshapes, landmarks, is_new_processing)
            
            # 3. EL ACELERADOR Y FRENO: Calculamos cuánto tiempo ha sobrado de este frame
            # y dormimos el hilo exactamente los milisegundos necesarios para ir a 60 FPS.
            elapsed_time = time.perf_counter() - loop_start
            time_left_to_sleep = (1.0 / self.target_fps) - elapsed_time
            
            if time_left_to_sleep > 0:
                time.sleep(time_left_to_sleep)

    def release_resources(self):
        self.is_running = False
        self.wait() # Espera a que el hilo termine limpiamente
        self.cam.stop()