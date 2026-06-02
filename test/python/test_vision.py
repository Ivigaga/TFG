import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from vision import VisionEngine

# --- FIXTURES ---

@pytest.fixture
@patch("vision.VisionEngine._initialize_detector")
@patch("vision.VisionEngine._initialize_camera")
def temp_vision(mock_init_cam, mock_init_detector):
    """
    Creates a VisionEngine without turning on the real webcam or loading the heavy ML model.
    """
    # 1. Configurar los mocks de inicialización para que devuelvan componentes falsos
    mock_cam = MagicMock()
    mock_init_cam.return_value = mock_cam
    
    mock_detector = MagicMock()
    mock_init_detector.return_value = mock_detector
    
    # 2. Instanciar el motor (no llamará al hardware real gracias a los parches)
    engine = VisionEngine(model_path="fake_path.task", target_fps=60)
    
    # 3. Interceptar la señal de PySide6 para poder espiarla
    engine.frame_processed = MagicMock()
    
    return engine


# --- CAMERA TESTS ---

@patch("vision.cv2.VideoCapture")
def test_initialize_camera_failure(mock_videocapture):
    """Verifies that the engine crashes safely and explicitly if no webcam is found."""
    # Hacer que la cámara de OpenCV siempre diga "no estoy disponible"
    mock_cap_instance = MagicMock()
    mock_cap_instance.isOpened.return_value = False
    mock_videocapture.return_value = mock_cap_instance
    
    # Interceptamos _initialize_detector para que no intente cargar la IA
    with patch("vision.VisionEngine._initialize_detector"):
        # Debería lanzar exactamente este error tras probar los 5 puertos
        with pytest.raises(Exception, match="CRITICAL ERROR: No camera detected."):
            VisionEngine(model_path="fake_path.task")
            
    # Verificamos que intentó buscar en los puertos 0, 1, 2, 3 y 4
    assert mock_videocapture.call_count == 5


# --- RUN LOOP TESTS ---

@patch("vision.time.perf_counter")
@patch("vision.cv2.cvtColor")
@patch("vision.cv2.flip")
@patch("vision.mp.Image")
def test_vision_run_loop_emits_frame(mock_mp_image, mock_flip, mock_cvt, mock_time, temp_vision):
    """Verifies that the infinite loop reads a frame, calls the AI, and emits the signal."""
    # 1. Crear un frame falso (una matriz de numpy simulando una imagen negra de OpenCV)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # TRUCO MÁGICO: Cuando el motor llame a cam.read(), le devolvemos el frame falso,
    # pero INMEDIATAMENTE apagamos el bucle (is_running = False) para que el hilo termine.
    def mock_read_side_effect():
        temp_vision.is_running = False
        return dummy_frame
    
    temp_vision.cam.read.side_effect = mock_read_side_effect
    
    # 2. Trucar el tiempo para forzar que (current_now - last_inference_time) dispare la IA
    mock_time.side_effect = [0.0, 1.0, 1.0] # start, current_now, elapsed
    
    # 3. Simular que la IA encontró una cara devolviendo resultados falsos
    fake_blendshape = MagicMock()
    fake_blendshape.category_name = "smile"
    fake_blendshape.score = 0.9
    
    temp_vision.current_result = MagicMock()
    temp_vision.current_result.face_blendshapes = [[fake_blendshape]]
    temp_vision.current_result.face_landmarks = [["fake_point_x", "fake_point_y"]]
    
    # 4. Ejecutar el bucle (solo dará 1 vuelta gracias a nuestro side_effect)
    temp_vision.run()
    
    # 5. Verificaciones
    # ¿Se envió a la IA?
    temp_vision.detector.detect_async.assert_called_once()
    
    # ¿La señal emitió los datos correctos al Presentador?
    temp_vision.frame_processed.emit.assert_called_once()
    
    # Recuperar los argumentos con los que se emitió la señal
    args, _ = temp_vision.frame_processed.emit.call_args
    emitted_frame, emitted_blendshapes, emitted_landmarks, is_new = args
    
    assert emitted_blendshapes["smile"] == 0.9
    assert emitted_landmarks == ["fake_point_x", "fake_point_y"]
    assert is_new is True


# --- RESOURCE MANAGEMENT TESTS ---

def test_release_resources(temp_vision):
    """Verifies that shutting down the engine correctly releases C++ and Hardware memory."""
    # Espiamos los métodos de control del hilo de Qt
    temp_vision.wait = MagicMock()
    temp_vision.quit = MagicMock()
    temp_vision.isRunning = MagicMock(return_value=True) # Simulamos que está atascado para forzar el quit()
    
    # Ejecutamos el apagado
    temp_vision.release_resources()
    
    # 1. ¿Apagó la cámara?
    temp_vision.cam.stop.assert_called_once()
    
    # 2. ¿Forzó la salida del QThread?
    temp_vision.quit.assert_called_once()
    
    # 3. ¿Cerró el detector de MediaPipe liberando la RAM?
    temp_vision.detector.close.assert_called_once()

# --- EDGE CASES & PERFORMANCE TESTS ---

@patch("vision.time.sleep")
def test_vision_run_loop_empty_frame(mock_sleep, temp_vision):
    """Verifies that if the camera fails to read a frame, it sleeps to prevent CPU overload."""
    # 1. Simulamos que la cámara se atasca y devuelve None
    def mock_read_side_effect():
        temp_vision.is_running = False  # Apagamos el bucle tras el primer intento
        return None
        
    temp_vision.cam.read.side_effect = mock_read_side_effect
    
    # 2. Ejecutamos
    temp_vision.run()
    
    # 3. Verificaciones
    # El código debe haber dormido el hilo 10ms (0.01) para no quemar la CPU con un while infinito
    mock_sleep.assert_called_with(0.01)
    
    # Ni la IA ni el emisor de frames debieron ejecutarse
    temp_vision.detector.detect_async.assert_not_called()
    temp_vision.frame_processed.emit.assert_not_called()


@patch("vision.time.perf_counter")
@patch("vision.cv2.cvtColor")
@patch("vision.cv2.flip")
def test_vision_run_loop_skips_inference_for_fps(mock_flip, mock_cvt, mock_time, temp_vision):
    """Verifies that if frames arrive too fast, it skips AI inference to save CPU but still renders."""
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def mock_read_side_effect():
        temp_vision.is_running = False
        return dummy_frame
        
    temp_vision.cam.read.side_effect = mock_read_side_effect
    
    # Simulamos el tiempo:
    # last_inference_time = 0.0 (por defecto)
    # current_now = 0.01 (Ha pasado menos de 1/60 segundos)
    mock_time.side_effect = [0.01, 0.01, 0.02]
    
    temp_vision.run()
    
    # La IA NO debió llamarse porque el frame llegó demasiado rápido
    temp_vision.detector.detect_async.assert_not_called()
    
    # Pero el frame SÍ debió emitirse para que la UI no se congele, enviando is_new_processing = False
    args, _ = temp_vision.frame_processed.emit.call_args
    emitted_frame, emitted_blendshapes, emitted_landmarks, is_new = args
    
    assert is_new is False


@patch("vision.time.perf_counter")
@patch("vision.cv2.cvtColor")
@patch("vision.cv2.flip")
@patch("vision.mp.Image")
def test_vision_emits_none_when_no_face(mock_mp_image, mock_flip, mock_cvt, mock_time, temp_vision):
    """Verifies that if the AI finds no faces (e.g. user leaves the room), it safely emits None."""
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    def mock_read_side_effect():
        temp_vision.is_running = False
        return dummy_frame
        
    temp_vision.cam.read.side_effect = mock_read_side_effect
    mock_time.side_effect = [0.0, 1.0, 1.0] 
    
    # Simulamos que la IA procesó la imagen, pero no encontró ninguna cara (listas vacías)
    temp_vision.current_result = MagicMock()
    temp_vision.current_result.face_blendshapes = []
    temp_vision.current_result.face_landmarks = []
    
    temp_vision.run()
    
    args, _ = temp_vision.frame_processed.emit.call_args
    emitted_frame, emitted_blendshapes, emitted_landmarks, is_new = args
    
    # El código debe ser a prueba de fallos y enviar None, no listas vacías ni errores
    assert emitted_blendshapes is None
    assert emitted_landmarks is None


@patch("vision.CameraStream")
@patch("vision.cv2.VideoCapture")
def test_initialize_camera_success_on_later_port(mock_videocapture, mock_camerastream):
    """Verifies that if port 0 is busy/broken, it automatically connects to port 1."""
    # 1. Creamos dos simulacros de cámara
    cam_fail = MagicMock()
    cam_fail.isOpened.return_value = False
    
    cam_success = MagicMock()
    cam_success.isOpened.return_value = True
    cam_success.read.return_value = (True, "fake_frame")
    
    # side_effect permite devolver valores secuenciales: primero falla, luego acierta
    mock_videocapture.side_effect = [cam_fail, cam_success]
    
    # Bloqueamos la inicialización del detector para no cargar la IA real
    with patch("vision.VisionEngine._initialize_detector"):
        engine = VisionEngine(model_path="fake.task")
        
    # Comprobamos que CameraStream se inicializó apuntando al puerto 1 (src=1)
    mock_camerastream.assert_called_once_with(src=1, target_fps=60)
    mock_camerastream.return_value.start.assert_called_once()