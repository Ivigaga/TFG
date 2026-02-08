import cv2
import mediapipe as mp
from pythonosc import udp_client # Librería para comunicación por red
import time

# --- 1. CONFIGURACIÓN DE RED (OSC/UDP) ---

IP = "127.0.0.1"  # Localhost (tu propio PC)
PORT = 7000       # Puerto donde escuchará Unreal Engine

print(f"Configurando cliente OSC en {IP}:{PORT}...")
client = udp_client.SimpleUDPClient(IP, PORT)
print("¡Cliente listo! Enviando datos...")

# --- 2. CONFIGURACIÓN MEDIAPIPE ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)

# --- 3. BUCLE PRINCIPAL ---
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir color para MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        
        # Volver a BGR para dibujar
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # --- LÓGICA DE ENVÍO DE DATOS ---
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Obtenemos la nariz (valores de 0.0 a 1.0)
            nariz_x = landmarks[mp_pose.PoseLandmark.NOSE.value].x
            nariz_y = landmarks[mp_pose.PoseLandmark.NOSE.value].y
            
            # ENVIAR A UNREAL:
            # Enviamos un mensaje con la "dirección" (etiqueta) y los valores
            # Unreal recibirá esto y sabrá que "/track/nariz" trae dos números
            client.send_message("/track/nariz", [nariz_x, nariz_y])
            
            # Visualización en Python (Debug)
            # Dibujamos los valores en pantalla para que sepas qué estás enviando
            texto_debug = f"X: {nariz_x:.2f} | Y: {nariz_y:.2f}"
            cv2.putText(image, texto_debug, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Dibujar el esqueleto
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        else:
            # Opcional: Enviar señal de que no hay usuario detectado
            client.send_message("/track/status", 0)

        cv2.imshow('Emisor OSC para Unreal (Q para salir)', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Transmisión finalizada.")