import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import vgamepad as vg
import time

# --- CONFIGURACIÓN ---
MODEL_PATH = 'face_landmarker.task' 
UMBRAL_BOCA = 0.4
UMBRAL_CEJAS = 0.7
UMBRAL_MORRITOS = 0.8
UMBRAL_SONRISA = 0.5


buttons={"guiño":vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "boca":vg.XUSB_BUTTON.XUSB_GAMEPAD_B, "cejas":vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "morritos":vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,"sonrisa":vg.XUSB_BUTTON.XUSB_GAMEPAD_B}


# Variables globales
RESULTADO_ACTUAL = None

def resultado_callback(result, output_image, timestamp_ms):
    global RESULTADO_ACTUAL
    RESULTADO_ACTUAL = result

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

    # 1. PASO CRUCIAL: Invertir AL PRINCIPIO
    # Ahora todo lo que hagamos (detectar y dibujar) será sobre la imagen espejo
    

    # Convertir para MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    frame_timestamp_ms = int(time.time() * 1000)

    detector.detect_async(mp_image, frame_timestamp_ms)

    if RESULTADO_ACTUAL and RESULTADO_ACTUAL.face_blendshapes:
        gestos = RESULTADO_ACTUAL.face_blendshapes[0]
        
        # --- 2. EL TRUCO DEL ESPEJO (SWAP LOGIC) ---
        # Como la imagen está invertida, MediaPipe se lía con izquierda/derecha.
        # Solución: Leemos la variable contraria.
        
        # Ceja: Si queremos detectar tu ceja REAL derecha, 
        # leemos lo que MediaPipe llama "OuterUpLeft" (porque está viendo un espejo)
        # Nota: Para las cejas usábamos el MAX de las dos, así que da igual.
        ceja_L = next((x.score for x in gestos if x.category_name == 'browOuterUpLeft'), 0.0)
        ceja_R = next((x.score for x in gestos if x.category_name == 'browOuterUpRight'), 0.0)
        val_cejas = max(ceja_L, ceja_R)

        # Sonrisa: (Da igual, es simétrica)
        smile_L = next((x.score for x in gestos if x.category_name == 'mouthSmileLeft'), 0.0)
        smile_R = next((x.score for x in gestos if x.category_name == 'mouthSmileRight'), 0.0)
        val_sonrisa = (smile_L + smile_R) / 2
        
        # Morritos y Boca: (Son gestos centrales, no afectan el espejo)
        val_boca = next((x.score for x in gestos if x.category_name == 'jawOpen'), 0.0)
        val_morritos = next((x.score for x in gestos if x.category_name == 'mouthPucker'), 0.0)

          # Usamos una forma optimizada de buscar los valores
        score_guiño = next((x.score for x in gestos if x.category_name == 'eyeBlinkRight'), 0.0)
        score_boca = next((x.score for x in gestos if x.category_name == 'jawOpen'), 0.0)

        if RESULTADO_ACTUAL.face_landmarks:
            nariz = RESULTADO_ACTUAL.face_landmarks[0][1] # Índice 1
            nariz_x=nariz.x
            nariz_y=nariz.y
            
        frame = cv2.flip(frame, 1)


        # --- AQUI ESTARÍA EL CAMBIO SI USARAS GUIÑOS ---
        # Si quisieras detectar guiño DERECHO real:
        # guiño_derecho_real = next((x.score for x in gestos if x.category_name == 'eyeBlinkLeft'), 0.0)
        # (Leemos el Left de la IA para obtener el Right Real)

        # --- 3. DIBUJAR TEXTO (Ahora saldrá bien) ---
        # Como estamos dibujando sobre el frame YA invertido, el texto sale derecho.

        # GESTO 1: BOCA -> BTN A
        if val_boca > UMBRAL_BOCA:
            gamepad.press_button(button=buttons["boca"])
            cv2.putText(frame, 'BTN A (BOCA)', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            gamepad.release_button(button=buttons["boca"])

        # GESTO 2: CEJAS -> BTN Y
        if val_cejas > UMBRAL_CEJAS:
            gamepad.press_button(button=buttons["cejas"])
            cv2.putText(frame, 'BTN Y (CEJAS)', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        else:
            gamepad.release_button(button=buttons["cejas"])

        # GESTO 3: MORRITOS -> BTN X
        if val_morritos > UMBRAL_MORRITOS:
            gamepad.press_button(button=buttons["morritos"])
            cv2.putText(frame, 'BTN X (MORRITOS)', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        else:
            gamepad.release_button(button=buttons["morritos"])

        # GESTO 4: SONRISA -> BTN B
        if val_sonrisa > UMBRAL_SONRISA:
            gamepad.press_button(button=buttons["sonrisa"])
            cv2.putText(frame, 'BTN B (SONRISA)', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        else:
            gamepad.release_button(button=buttons["sonrisa"])

            # 1. GUIÑO IZQUIERDO -> Botón A
        if score_guiño > 0.5:
            gamepad.press_button(button=buttons["guiño"])
            cv2.putText(frame, 'BTN A (GUIÑO)', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            gamepad.release_button(button=buttons["guiño"])

        joystick_x = 0
        joystick_y = 0
        if RESULTADO_ACTUAL.face_landmarks:
            if nariz_x > 0.6:
                joystick_x = -20000
                cv2.putText(frame, '< IZQUIERDA', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif nariz_x < 0.4:
                joystick_x = 20000
                cv2.putText(frame, 'DERECHA >', (frame.shape[1]-200, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            if nariz_y > 0.6:
                joystick_y = -20000
                cv2.putText(frame, 'ABAJO', (frame.shape[1]//2 - 50, frame.shape[0]-50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            elif nariz_y < 0.4:
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