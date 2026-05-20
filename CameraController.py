import json
import os
import sys
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import vgamepad as vg
import time
from CameraStream import CameraStream





def resolver_ruta(ruta_relativa):
    """Obtiene la ruta absoluta al recurso, sin importar dónde se mueva la carpeta"""
    if getattr(sys, 'frozen', False):
        ruta_base = os.path.dirname(sys.executable)
        ruta_completa = os.path.join(ruta_base, ruta_relativa)
        if not os.path.exists(ruta_completa) and hasattr(sys, '_MEIPASS'):
            ruta_completa = os.path.join(sys._MEIPASS, ruta_relativa)
        return ruta_completa
    else:
        return os.path.join(os.path.abspath("."), ruta_relativa)

# --- CONFIGURACIÓN GLOBAL ---
CONTINUOS_MODE = True
TIME_DURATION_SECONDS = 0.05
MODEL_PATH = resolver_ruta('face_landmarker.task')
TARGET_FPS = 60

CURRENT_RESULT = None
gamepad = vg.VX360Gamepad()

def resultado_callback(result, output_image, timestamp_ms):
    global CURRENT_RESULT
    CURRENT_RESULT = result

# --- FUNCIONES DE CONTROL ---
def changeMovementMode(input_data, frame):
    global CONTINUOS_MODE
    if input_data.get("score", 0) > input_data["threshold"]:
        if not input_data["active"]:
            CONTINUOS_MODE = not CONTINUOS_MODE
            input_data["active"] = True
    else:
        input_data["active"] = False
    
    texto_modo = "CONTINUO" if CONTINUOS_MODE else "PASOS"
    color = (0, 255, 0) if CONTINUOS_MODE else (0, 165, 255)
    cv2.putText(frame, f'MODO: {texto_modo}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def pushInputButton(input_data, frame):
    if input_data.get("score", 0) > input_data["threshold"]:
        gamepad.press_button(button=input_data["input"])
        input_data["active"] = True
        cv2.putText(frame, f'BTN ACTIVADO', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        gamepad.release_button(button=input_data["input"])
        input_data["active"] = False

# Mapeo de texto a función de Python
FUNCIONES_MAP = {
    "pushInputButton": pushInputButton,
    "changeMovementMode": changeMovementMode
}

# Mapeo de texto a botón de vgamepad
BOTONES_MAP = {
    "XUSB_GAMEPAD_B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "XUSB_GAMEPAD_START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "XUSB_GAMEPAD_BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "XUSB_GAMEPAD_A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A
}

# Para facilitar el guardado, creamos un mapeo inverso de los botones (de valor a texto)
BOTONES_INVERSE_MAP = {v: k for k, v in BOTONES_MAP.items()}

INPUT_STRUCTURE = {}

def encontrar_camara_activa():
    print("Buscando cámara disponible...")
    for indice in range(5):
        cap = cv2.VideoCapture(indice)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"¡Cámara encontrada en el puerto/índice {indice}!")
                cap.release()
                return indice
        cap.release()
    print("ERROR CRÍTICO: No se ha detectado ninguna cámara.")
    return 0

def initialice():
    global CURRENT_RESULT
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        result_callback=resultado_callback,
        output_face_blendshapes=True,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)
    cam = CameraStream(src=encontrar_camara_activa()).start()
    print(f"Sistema High-Performance. Target: {TARGET_FPS} FPS.")
    return detector, cam

def read_gestures(gestures):
    INPUT_STRUCTURE["eyeBrowsUp"]["score"] = max(gestures["browOuterUpLeft"], gestures["browOuterUpRight"])
    INPUT_STRUCTURE["smile"]["score"] = (gestures["mouthSmileLeft"] + gestures["mouthSmileRight"]) / 2
    INPUT_STRUCTURE["mouthPucker"]["score"] = gestures["mouthPucker"]
    INPUT_STRUCTURE["eyeBlinkRight"]["score"] = gestures["eyeBlinkRight"]
    INPUT_STRUCTURE["jawOpen"]["score"] = gestures["jawOpen"]

def move_left_joystick(x, y, start_time, frame):
    jx, jy = 0, 0
    movinx, moviny = False, False
    
    if x > INPUT_STRUCTURE["noseLeft"]["threshold"]: 
        jx = -20000 
        movinx = True
    elif x < INPUT_STRUCTURE["noseRight"]["threshold"]: 
        jx = 20000
        movinx = True
        
    if y > INPUT_STRUCTURE["noseDown"]["threshold"]: 
        jy = -20000
        moviny = True
    elif y < INPUT_STRUCTURE["noseUp"]["threshold"]: 
        jy = 20000
        moviny = True

    if not CONTINUOS_MODE and (INPUT_STRUCTURE["noseUp"]["active"] is True or INPUT_STRUCTURE["noseDown"]["active"] is True):
        jy = 0

    INPUT_STRUCTURE["noseLeft"]["active"] = movinx
    INPUT_STRUCTURE["noseRight"]["active"] = movinx
    INPUT_STRUCTURE["noseUp"]["active"] = moviny
    INPUT_STRUCTURE["noseDown"]["active"] = moviny

    gamepad.left_joystick(x_value=jx, y_value=jy)


def save_inputs_to_file(file_path="default_inputs.json"):
    file_json={}
    for gesture, data in INPUT_STRUCTURE.items():
        file_json[gesture] = {}
        for key, value in data.items():
            if key == "function" and value is not None:
                # Obtenemos el nombre de la función (ej. "pushInputButton")
                file_json[gesture][key] = value.__name__
                
            elif key == "input" and value is not None:
                # Buscamos el nombre del botón en texto usando el mapa inverso
                file_json[gesture][key] = BOTONES_INVERSE_MAP.get(value, None)
                
            else:
                # Guardamos thresholds, actives y scores tal cual (son números/booleanos)
                file_json[gesture][key] = value

    with open(file_path, 'w') as f:
        json.dump(file_json, f, indent=4)

def load_inputs_from_file(file_path="default_inputs.json"):
    global INPUT_STRUCTURE

    with open(file_path, 'r') as f:
        file_json = json.load(f)
    temp_structure = {}
    for gesture, data in file_json.items():
        temp_structure[gesture] = {}
        for key, value in data.items():
            if key == "function" and value is not None:
                temp_structure[gesture][key] = FUNCIONES_MAP.get(value, None)
                
            elif key == "input" and value is not None:
                temp_structure[gesture][key] = BOTONES_MAP.get(value, None)
                
            else:
                temp_structure[gesture][key] = value

    INPUT_STRUCTURE = temp_structure

# --- CLASE CONTROLADORA PARA LA GUI ---
class GestosControlador:
    def __init__(self):
        self.detector, self.cam = initialice()
        self.last_inference_time = 0
        self.y_activation_start_time = None
        self.prev_time = 0
        load_inputs_from_file()

    def procesar_frame_unico(self):
        loop_start = time.perf_counter()
        
        frame = self.cam.read()
        if frame is None:
            return None

        # 1. INFERENCIA LIGERA
        current_now = time.perf_counter()
        if (current_now - self.last_inference_time) > 0.033:
            rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_small)
            self.detector.detect_async(mp_image, int(current_now * 1000))
            self.last_inference_time = current_now

        frame = cv2.flip(frame, 1)

        # 2. LÓGICA DE CONTROL
        if CURRENT_RESULT and CURRENT_RESULT.face_blendshapes:
            gestures = {cat.category_name: cat.score for cat in CURRENT_RESULT.face_blendshapes[0]}
            read_gestures(gestures)

            for key, input in INPUT_STRUCTURE.items():
                if "function" in input and input["function"]!=None and "score" in input:
                    input["function"](input,frame)

            if CURRENT_RESULT.face_landmarks:
                nose = CURRENT_RESULT.face_landmarks[0][1]
                move_left_joystick(nose.x, nose.y, self.y_activation_start_time, frame)
            
            gamepad.update()

        # 3. FPS Info (Opcional, para mantener tu texto original)
        fps = 1.0 / (loop_start - self.prev_time) if self.prev_time > 0 else TARGET_FPS
        cv2.putText(frame, f'FPS: {int(fps)}', (frame.shape[1]-120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        self.prev_time = loop_start

        return frame
    
    def getGestureForButton(self, button):
        for gesture, data in INPUT_STRUCTURE.items():
            if BOTONES_INVERSE_MAP.get(data.get("input")) == button:
                return gesture
        return None

    def cerrar_recursos(self):
        self.cam.stop()
        gamepad.reset()
        gamepad.update()



