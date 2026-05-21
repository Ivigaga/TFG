import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from CameraStream import CameraStream

class VisionEngine:
    def __init__(self, model_path, target_fps=60):
        self.target_fps = target_fps
        self.last_inference_time = 0
        self.timestamp_ms = 0
        
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
                    return CameraStream(src=index).start()
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

    def get_processed_frame(self):
        """Fetches a frame, runs inference, and returns (frame, blendshapes, landmarks, is_new_processing)"""
        frame = self.cam.read()
        if frame is None:
            return None, None, None, False

        is_new_processing = False  # <-- Inicializamos el chivato
        current_now = time.perf_counter()
        
        # Solo procesamos si ha pasado el tiempo marcado por TARGET_FPS
        if (current_now - self.last_inference_time) > (1 / self.target_fps):
            rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_small)
            
            self.timestamp_ms += int(1000 / self.target_fps)
            self.detector.detect_async(mp_image, self.timestamp_ms)
            self.last_inference_time = current_now
            is_new_processing = True  # <-- Marcamos que SÍ hemos procesado IA

        frame = cv2.flip(frame, 1)
        
        blendshapes = None
        landmarks = None
        
        if self.current_result:
            if self.current_result.face_blendshapes:
                blendshapes = {cat.category_name: cat.score for cat in self.current_result.face_blendshapes[0]}
            if self.current_result.face_landmarks:
                landmarks = self.current_result.face_landmarks[0]

        # Devolvemos el booleano al final
        return frame, blendshapes, landmarks, is_new_processing

    def release_resources(self):
        self.cam.stop()