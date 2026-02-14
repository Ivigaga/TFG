import cv2
import mediapipe as mp
from functools import partial
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import vgamepad as vg
import time

CONTINUOS_MODE = True
# A 30 FPS, 4 frames son aprox 133ms. Ideal para un "toque" de GameBoy.
TIME_DURATION_SECONDS = 0.05

def changeMovementMode(input, frame):
    if input["score"] > input["threshold"]:
        if not input["active"]:
            global CONTINUOS_MODE
            CONTINUOS_MODE = not CONTINUOS_MODE
            input["active"] = True
    else:
        input["active"] = False
    
    # Dibujamos siempre el estado
    texto_modo = "CONTINUO" if CONTINUOS_MODE else "PASOS"
    color = (0, 255, 0) if CONTINUOS_MODE else (0, 165, 255)
    cv2.putText(frame, f'MODO: {texto_modo}', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def pushInputButton(input, frame):
    if input["score"] > input["threshold"]:
        gamepad.press_button(button=input["input"])
        input["active"] = True
        cv2.putText(frame, f'BTN ACTIVADO', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        gamepad.release_button(button=input["input"])
        input["active"] = False

# --- CONFIGURACIÓN ---
MODEL_PATH = 'face_landmarker.task' 
INPUT_STRUCTURE={"jawOpen":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_B,"threshold":0.3,"active":True},"eyeBrowsUp":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_START,"threshold":0.4,"active":True},"mouthPucker":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,"threshold":0.8,"active":True},"smile":{"function":changeMovementMode,"input":None,"threshold":0.5,"active":False},"eyeBlinkRight":{"function":pushInputButton,"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_A,"threshold":0.6,"active":True},"noseLeft":{"function":None,"input":None,"threshold":0.6,"active":False},"noseRight":{"function":None,"input":None,"threshold":0.4,"active":False},"noseUp":{"function":None,"input":None,"threshold":0.4,"active":False},"noseDown":{"function":None,"input":None,"threshold":0.6,"active":False}}

# Variables globales
CURRENT_RESULT = None

def resultado_callback(result, output_image, timestamp_ms):
    global CURRENT_RESULT
    CURRENT_RESULT = result

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback=resultado_callback,
    output_face_blendshapes=True,
    num_faces=1
)

detector = vision.FaceLandmarker.create_from_options(options)
gamepad = vg.VX360Gamepad()
cap = cv2.VideoCapture(0)

print("Sistema Espejo Corregido.")

def main():
    y_activation_start_time = None
    
    # Para calcular FPS
    prev_time = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        # Calculo de FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
        prev_time = curr_time

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        frame_timestamp_ms = int(time.time() * 1000)

        detector.detect_async(mp_image, frame_timestamp_ms)

        # Invertir frame AL PRINCIPIO
        frame = cv2.flip(frame, 1)

        if CURRENT_RESULT and CURRENT_RESULT.face_blendshapes:
            gestures = CURRENT_RESULT.face_blendshapes[0]
            
            # --- LECTURA DE VALORES ---
            eyebrow_up_L = next((x.score for x in gestures if x.category_name == 'browOuterUpLeft'), 0.0)
            eyebrow_up_R = next((x.score for x in gestures if x.category_name == 'browOuterUpRight'), 0.0)
            val_eyebrows_up = max(eyebrow_up_L, eyebrow_up_R)
            INPUT_STRUCTURE["eyeBrowsUp"]["score"] = val_eyebrows_up
            
            smile_L = next((x.score for x in gestures if x.category_name == 'mouthSmileLeft'), 0.0)
            smile_R = next((x.score for x in gestures if x.category_name == 'mouthSmileRight'), 0.0)
            val_smile = (smile_L + smile_R) / 2
            INPUT_STRUCTURE["smile"]["score"] = val_smile
            
            val_mouth_pucker = next((x.score for x in gestures if x.category_name == 'mouthPucker'), 0.0)
            INPUT_STRUCTURE["mouthPucker"]["score"] = val_mouth_pucker
            
            score_right_twink = next((x.score for x in gestures if x.category_name == 'eyeBlinkRight'), 0.0)
            INPUT_STRUCTURE["eyeBlinkRight"]["score"] = score_right_twink
            
            score_open_mouth = next((x.score for x in gestures if x.category_name == 'jawOpen'), 0.0)
            INPUT_STRUCTURE["jawOpen"]["score"] = score_open_mouth

            # HE QUITADO EL PRINT DEL BUCLE PARA AUMENTAR FPS
            
            nose_x = 0
            nose_y = 0
            
            if CURRENT_RESULT.face_landmarks:
                nose = CURRENT_RESULT.face_landmarks[0][1] 
                nose_x = nose.x
                nose_y = nose.y

            # Ejecutar funciones de botones
            for key, input in INPUT_STRUCTURE.items():
                if input["function"] is not None and "score" in input:
                    input["function"](input, frame)
        
            is_activating_y = (nose_y > INPUT_STRUCTURE["noseDown"]["threshold"] or 
                               nose_y < INPUT_STRUCTURE["noseUp"]["threshold"])
            
            # Lógica del cronómetro
            if is_activating_y:
                # Si acabamos de empezar a movernos y el cronómetro estaba apagado, lo encendemos
                if y_activation_start_time is None:
                    y_activation_start_time = time.time()
            else:
                # Si volvemos al centro, reseteamos el cronómetro a None
                y_activation_start_time = None
            # Lógica Joystick
            if CURRENT_RESULT.face_landmarks:
                move_left_joystick(nose_x, nose_y, y_activation_start_time, frame)
  
                    
            gamepad.update()

        # Mostrar FPS
        cv2.putText(frame, f'FPS: {int(fps)}', (frame.shape[1]-100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow('Control Espejo Correcto', frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    gamepad.reset()
    gamepad.update()

def move_left_joystick(x, y, start_time=None, frame=None):
    joystick_x = 0
    joystick_y = 0
    
    if x > INPUT_STRUCTURE["noseLeft"]["threshold"]:
        joystick_x = -20000
        cv2.putText(frame, '< IZQUIERDA', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    elif x < INPUT_STRUCTURE["noseRight"]["threshold"]:
        joystick_x = 20000
        cv2.putText(frame, 'DERECHA >', (frame.shape[1]-200, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
    if y > INPUT_STRUCTURE["noseDown"]["threshold"]:
        joystick_y = -20000
        cv2.putText(frame, 'ABAJO', (frame.shape[1]//2 - 50, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    elif y < INPUT_STRUCTURE["noseUp"]["threshold"]:
        joystick_y = 20000
        cv2.putText(frame, 'ARRIBA', (frame.shape[1]//2 - 50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    if CONTINUOS_MODE == False and start_time is not None:
        # Calculamos cuánto tiempo ha pasado desde que activaste la nariz
        elapsed_time = time.time() - start_time
        
        # Si ha pasado más tiempo del permitido (0.15s), cortamos la señal
        if elapsed_time > TIME_DURATION_SECONDS:
            joystick_y = 0
            # Opcional: Feedback visual para ti
            cv2.putText(frame, 'CORTADO (TIEMPO)', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    gamepad.left_joystick(x_value=joystick_x, y_value=joystick_y)

if __name__ == "__main__":
    main()