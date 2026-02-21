import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import vgamepad as vg
import time
from CameraStream import CameraStream

# --- CONFIGURACIÓN GLOBAL ---
CONTINUOS_MODE = True
TIME_DURATION_SECONDS = 0.05
MODEL_PATH = 'face_landmarker.task' 
TARGET_FPS = 45  # Súbelo a 60; si el PC no llega, irá al máximo posible sin "quedarse dormido"

CURRENT_RESULT = None
gamepad = vg.VX360Gamepad()

def resultado_callback(result, output_image, timestamp_ms):
    global CURRENT_RESULT
    CURRENT_RESULT = result

# --- ESTRUCTURA Y FUNCIONES ---
def changeMovementMode(input_data, frame):
    if input_data.get("score", 0) > input_data["threshold"]:
        if not input_data["active"]:
            global CONTINUOS_MODE
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

INPUT_STRUCTURE={
    "jawOpen":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_B,"threshold":0.5,"active":False},
    "eyeBrowsUp":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_START,"threshold":0.4,"active":False},
    "mouthPucker":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,"threshold":0.8,"active":False},
    "smile":{"function":changeMovementMode,"input":None,"threshold":0.5,"active":False},
    "eyeBlinkRight":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_A,"threshold":0.6,"active":False},
    "noseLeft":{"threshold":0.6}, "noseRight":{"threshold":0.4},
    "noseUp":{"threshold":0.4}, "noseDown":{"threshold":0.6}
}

def main():
    detector, cam, frame_target_time, prev_time, last_inference_time, y_activation_start_time = initialice()
    try:
        while True:
            loop_start = time.perf_counter()

            frame = cam.read()
            if frame is None: continue

            # 1. INFERENCIA LIGERA (Resize agresivo)
            current_now = time.perf_counter()
            if (current_now - last_inference_time) > 0.033: # Máximo 30 inferencias por seg
                
                rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_small)
                detector.detect_async(mp_image, int(current_now * 1000))
                last_inference_time = current_now

            frame = cv2.flip(frame, 1)

            # 2. LÓGICA DE CONTROL (Solo si hay datos, pero el frame NO espera)
            if CURRENT_RESULT and CURRENT_RESULT.face_blendshapes:
                gestures = {cat.category_name: cat.score for cat in CURRENT_RESULT.face_blendshapes[0]}
                
                # Mapeo de scores
                read_gestures(gestures)

                # Ejecutamos funciones de cada input
                for key in ["jawOpen", "eyeBrowsUp", "mouthPucker", "smile", "eyeBlinkRight"]:
                    INPUT_STRUCTURE[key]["function"](INPUT_STRUCTURE[key], frame)

                # Control del joystick basado en la posición de la nariz
                if CURRENT_RESULT.face_landmarks:
                    nose = CURRENT_RESULT.face_landmarks[0][1]
                    # Joystick
                    move_left_joystick(nose.x, nose.y, y_activation_start_time, frame)
                
                gamepad.update()

            # 3. ESPERA ACTIVA (Busy Wait) - Esto evita el lag de Windows
            # En lugar de sleep(), nos quedamos en un bucle vacío hasta que sea el momento
            while (time.perf_counter() - loop_start) < frame_target_time:
                pass # Consume CPU pero garantiza FPS exactos

            # 4. FPS REALES
            actual_now = time.perf_counter()
            fps = 1.0 / (actual_now - prev_time)
            prev_time = actual_now
            
            cv2.putText(frame, f'FPS: {int(fps)}', (frame.shape[1]-120, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.imshow('Control Turbo Precise', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cleanup(cam)

def cleanup(cam):
    cam.stop()
    cv2.destroyAllWindows()
    gamepad.reset()
    gamepad.update()

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
    cam = CameraStream(src=0).start()
    
    frame_target_time = 1.0 / TARGET_FPS
    prev_time = time.perf_counter() # Usamos perf_counter para máxima precisión
    last_inference_time = 0
    y_activation_start_time = None

    print(f"Sistema High-Performance. Target: {TARGET_FPS} FPS.")
    return detector,cam,frame_target_time,prev_time,last_inference_time,y_activation_start_time

def read_gestures(gestures):
    INPUT_STRUCTURE["eyeBrowsUp"]["score"] = max(gestures["browOuterUpLeft"], gestures["browOuterUpRight"])
    INPUT_STRUCTURE["smile"]["score"] = (gestures["mouthSmileLeft"] + gestures["mouthSmileRight"]) / 2
    INPUT_STRUCTURE["mouthPucker"]["score"] = gestures["mouthPucker"]
    INPUT_STRUCTURE["eyeBlinkRight"]["score"] = gestures["eyeBlinkRight"]
    INPUT_STRUCTURE["jawOpen"]["score"] = gestures["jawOpen"]

def move_left_joystick(x, y, start_time, frame):
    jx, jy = 0, 0
    if x > INPUT_STRUCTURE["noseLeft"]["threshold"]: jx = -20000
    elif x < INPUT_STRUCTURE["noseRight"]["threshold"]: jx = 20000
    if y > INPUT_STRUCTURE["noseDown"]["threshold"]: jy = -20000
    elif y < INPUT_STRUCTURE["noseUp"]["threshold"]: jy = 20000

    # Lógica de pasos simplificada
    if not CONTINUOS_MODE and jy != 0:
        cv2.putText(frame, 'MODO PASOS', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    gamepad.left_joystick(x_value=jx, y_value=jy)

if __name__ == "__main__":
    main()