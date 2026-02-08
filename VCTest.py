import vgamepad as vg
import time

# 1. Inicializar el mando virtual (Emularemos un mando de Xbox 360)
gamepad = vg.VX360Gamepad()

print("Mando virtual conectado. Esperando 2 segundos...")
time.sleep(2)

# --- EJEMPLO DE USO ---

# Digamos que tu cámara detecta: "Inclinación a la derecha"
# Quieres mover el Stick Izquierdo (Left Joystick) a la derecha.

# Los valores van de -32768 a 32767 (para ejes X e Y)
# X: -32768 (Izquierda) a 32767 (Derecha)
# Y: -32768 (Abajo) a 32767 (Arriba)

def aplicar_movimiento_camara(valor_x, valor_y):
    # Convertir tus valores de cámara a valores de Joystick
    gamepad.left_joystick(x_value=valor_x, y_value=valor_y)
    gamepad.update() # IMPORTANTE: Enviar el estado al sistema

# Simulación: Mover a la derecha suavemente
print("Moviendo a la derecha...")
aplicar_movimiento_camara(30000, 0)
time.sleep(1)

for i in range(15):
    # Simulación: Presionar el botón 'A' (saltar)
    print("Presionando botón A...")
    gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    time.sleep(0.1) # Breve pausa para que el juego lo registre
    gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()

# Resetear el mando a estado neutral al cerrar o dejar de detectar
print("Soltando controles...")
gamepad.reset()
gamepad.update()