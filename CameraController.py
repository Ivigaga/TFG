import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import vgamepad as vg
import time

# --- CONFIGURACIÓN ---
MODEL_PATH = 'face_landmarker.task' 
input_structure={"jawOpen":{"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_B,"threshold":0.4},"eyeBrowsUp":{"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_START,"threshold":0.4},"mouthPucker":{"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,"threshold":0.8},"smile":{"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_B,"threshold":0.5},"eyeBlinkRight":{"input":vg.XUSB_BUTTON.XUSB_GAMEPAD_A,"threshold":0.5}}

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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break


    

    # Convertir para MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    frame_timestamp_ms = int(time.time() * 1000)

    detector.detect_async(mp_image, frame_timestamp_ms)

    if CURRENT_RESULT and CURRENT_RESULT.face_blendshapes:
        gestures = CURRENT_RESULT.face_blendshapes[0]
        
        # --- 2. EL TRUCO DEL ESPEJO (SWAP LOGIC) ---
        # Como la imagen está invertida, MediaPipe se lía con izquierda/derecha.
        # Solución: Leemos la variable contraria.
        
        # Ceja: Si queremos detectar tu ceja REAL derecha, 
        # leemos lo que MediaPipe llama "OuterUpLeft" (porque está viendo un espejo)
        # Nota: Para las cejas usábamos el MAX de las dos, así que da igual.
        eyebrow_up_L = next((x.score for x in gestures if x.category_name == 'browOuterUpLeft'), 0.0)
        eyebrow_up_R = next((x.score for x in gestures if x.category_name == 'browOuterUpRight'), 0.0)
        val_eyebrows_up = max(eyebrow_up_L, eyebrow_up_R)

        # Sonrisa: (Da igual, es simétrica)
        smile_L = next((x.score for x in gestures if x.category_name == 'mouthSmileLeft'), 0.0)
        smile_R = next((x.score for x in gestures if x.category_name == 'mouthSmileRight'), 0.0)
        val_smile = (smile_L + smile_R) / 2
        
        # Morritos y Boca: (Son gestos centrales, no afectan el espejo)
        val_mouth_pucker = next((x.score for x in gestures if x.category_name == 'mouthPucker'), 0.0)

        # Usamos una forma optimizada de buscar los valores
        score_right_twink = next((x.score for x in gestures if x.category_name == 'eyeBlinkRight'), 0.0)
        score_open_mouth = next((x.score for x in gestures if x.category_name == 'jawOpen'), 0.0)

        if CURRENT_RESULT.face_landmarks:
            nose = CURRENT_RESULT.face_landmarks[0][1] # Índice 1
            nose_x=nose.x
            nose_y=nose.y
            
        frame = cv2.flip(frame, 1)


        # --- 3. DIBUJAR TEXTO (Ahora saldrá bien) ---
        # Como estamos dibujando sobre el frame YA invertido, el texto sale derecho.
        if score_open_mouth > input_structure["jawOpen"]["threshold"]:
            gamepad.press_button(button=input_structure["jawOpen"]["input"])
            cv2.putText(frame, 'BTN A (BOCA)', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            gamepad.release_button(button=input_structure["jawOpen"]["input"])


        if val_eyebrows_up > input_structure["eyeBrowsUp"]["threshold"]:
            gamepad.press_button(button=input_structure["eyeBrowsUp"]["input"])
            cv2.putText(frame, 'BTN Y (CEJAS)', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        else:
            gamepad.release_button(button=input_structure["eyeBrowsUp"]["input"])

        if val_mouth_pucker > input_structure["mouthPucker"]["threshold"]:
            gamepad.press_button(button=input_structure["mouthPucker"]["input"])
            cv2.putText(frame, 'BTN X (MORRITOS)', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        else:
            gamepad.release_button(button=input_structure["mouthPucker"]["input"])


        if val_smile > input_structure["smile"]["threshold"]:
            gamepad.press_button(button=input_structure["smile"]["input"])
            cv2.putText(frame, 'BTN B (SONRISA)', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            gamepad.release_button(button=input_structure["smile"]["input"])


        if score_right_twink > input_structure["eyeBlinkRight"]["threshold"]:
            gamepad.press_button(button=input_structure["eyeBlinkRight"]["input"])
            cv2.putText(frame, 'BTN A (GUIÑO)', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            gamepad.release_button(button=input_structure["eyeBlinkRight"]["input"])

        joystick_x = 0
        joystick_y = 0
        if CURRENT_RESULT.face_landmarks:
            if nose_x > 0.6:
                joystick_x = -20000
                cv2.putText(frame, '< IZQUIERDA', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif nose_x < 0.4:
                joystick_x = 20000
                cv2.putText(frame, 'DERECHA >', (frame.shape[1]-200, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            if nose_y > 0.6:
                joystick_y = -20000
                cv2.putText(frame, 'ABAJO', (frame.shape[1]//2 - 50, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif nose_y < 0.4:
                joystick_y = 20000
                cv2.putText(frame, 'ARRIBA', (frame.shape[1]//2 - 50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            

            gamepad.left_joystick(x_value=joystick_x, y_value=joystick_y)
                
            
        gamepad.update()

    cv2.imshow('Control Espejo Correcto', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
gamepad.reset()
gamepad.update()