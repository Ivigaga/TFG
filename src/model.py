"""
Módulo Modelo - Capa de Persistencia de Datos de la Arquitectura MVP

Responsabilidades principales:
  - Gestionar estructura de entrada de gestos (input_structure.json)
  - Mantener puntuaciones de gestos en tiempo real desde MediaPipe
  - Manejar mapeo de gestos a entrada de mando (XUSB_GAMEPAD_*)
  - Gestión de perfiles de usuario (guardar/cargar configuraciones)
  - Detección automática de juegos Steam y escaneo de ROMs
  - Configuración de emuladores por consola
  - Estado de sistema (modo tutorial, modo continuo vs pasos)

Características principales:
  - Estructura de datos de gestos con umbrales configurables
  - Cálculo de puntuaciones de gestos desde BlendShapes de MediaPipe
  - Sistema de caché para ROMs (evita re-escaneo en cada carga)
  - Escaneo inteligente de Steam (lectura de VDF, descarga de logos)
  - Soporte para múltiples librerías de Steam
  - Configuración persistente (JSON)
  - Gestión de tutorial y estado de primer uso
"""

import csv
import ctypes
import datetime
import json
import os
import sys

def get_asset_path(relative_path):
    """
    Resolver ruta a archivos de solo lectura que vienen empaquetados (IA, estilos, iconos fijos).
    
    Nota: Usar SOLO para archivos que se distribuyen con la aplicación y NO cambian.
    Para archivos de usuario (perfiles, ROMs), usar get_save_path() en su lugar.
    
    Args:
        relative_path: str - ruta relativa desde /conf (ej: "images/gestures/smile.png")
    
    Returns:
        str - ruta absoluta del archivo
    
    Comportamiento:
        - Si está empaquetado (PyInstaller): usa sys._MEIPASS (carpeta _internal)
        - En desarrollo: sube un nivel desde /src y entra en /conf
    """
    if getattr(sys, 'frozen', False):
        # sys._MEIPASS apunta directamente a la carpeta _internal de PyInstaller
        base_path = sys._MEIPASS
    else:
        # En desarrollo, subimos un nivel desde /src y entramos en /conf
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))
    return os.path.join(base_path, relative_path)

def get_save_path(relative_path):
    """
    Resolver ruta a archivos de escritura/usuario (JSONs, perfiles, portadas descargadas).
    
    Nota: Usar SOLO para archivos que el usuario modifica o que la app genera.
    Para archivos estáticos (modelos IA), usar get_asset_path() en su lugar.
    
    Args:
        relative_path: str - ruta relativa desde /conf (ej: "controls/perfil_usuario.json")
    
    Returns:
        str - ruta absoluta del archivo
    
    Comportamiento:
        - Si está empaquetado (PyInstaller): usa directorio del .exe (fácil acceso para datos)
        - En desarrollo: sube un nivel desde /src y entra en /conf (mismo que get_asset_path)
    """
    if getattr(sys, 'frozen', False):
        # sys.executable apunta a la raíz donde está el .exe, ideal para guardar datos
        base_path = os.path.dirname(sys.executable)
    else:
        # En desarrollo, subimos un nivel desde /src y entramos en /conf
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))
    return os.path.join(base_path, relative_path)

class AppModel:
    """
    Capa de modelo implementando persistencia de datos y gestión de estado de la aplicación.
    
    Gestiona:
    - Estructura de mapeo de gestos a entrada de mando
    - Puntuaciones de gestos en tiempo real
    - Perfiles de usuario (guardar/cargar)
    - Configuración de emuladores
    - Catálogo de juegos (Steam + ROMs)
    - Estado de tutorial y primera ejecución
    """
    
    def __init__(self, json_path="controls/default_inputs.json"):
        """
        Inicializar el modelo con rutas de archivo y cargar configuración.
        
        Args:
            json_path: str - archivo de configuración de gestos (relativo a /conf)
        
        Inicializa:
            - Rutas de archivos (configuración, perfiles, juegos, emuladores)
            - Estructura de entrada de gestos desde JSON
            - Variables de estado (modo continuo, FPS objetivo, etc.)
            - Rutas de modelos IA (MediaPipe face_landmarker.task)
            - Directorios de usuario (controls, games)
            - Caché de ROMs para evitar re-escaneo
            - Estado de tutorial desde app_settings.json
        """
        # === Rutas de Configuración ===
        self.json_path = get_save_path(json_path)  # Archivo actual de mapeo de gestos
        self.default_json_path = get_save_path("controls/default_inputs.json")  # Plantilla de defecto
        self.settings_path = get_save_path("app_settings.json")  # Estado global (tutorial, etc.)
        
        # === Estado de la Aplicación ===
        self.is_first_run_session = True  # Bandera de tutorial (cargada desde app_settings.json)
        self.input_structure = {}  # Estructura principal: {"gesture_name": {"input": "XUSB_*", ...}}
        self.is_continuous_mode = True  # Modo navegación: continuo (libre) vs pasos (discreto)
        self.target_fps = 60  # FPS objetivo del motor de visión
        
        # === Rutas de Archivos ===
        self.model_path = get_asset_path('face_landmarker.task')  # Modelo MediaPipe (solo lectura)
        
        # === Directorios de Usuario ===
        self.controls_dir = get_save_path('controls')  # Perfiles de usuario (JSON)
        os.makedirs(self.controls_dir, exist_ok=True)
        self.games_dir = get_save_path('games')  # Base de datos de juegos
        os.makedirs(self.games_dir, exist_ok=True)
        
        # === Archivos de Juegos ===
        self.rom_folders_file = get_save_path('games/rom_folders.json')  # Carpetas donde buscar ROMs
        self.steam_games_file = get_save_path('games/steam_games.json')  # BD consolidada de juegos Steam
        
        # === Configuración de Emuladores ===
        self.emulators_file = get_save_path('games/emulators.json')  # Ruta de ejecutables por consola
        self.emulators_config = self._load_emulators_config()  # Cargar configuración desde disco
        
        # === Caché ===
        self._cached_roms = None  # Almacenamiento en memoria de ROMs escaneadas (evita re-escaneo)

        # === SISTEMA DE TELEMETRÍA (NUEVO) ===
        self.test_mode = False
        self.telemetry = {
            "tutorial_time_seconds": 0.0,
            "back_from_gestures_count": 0,
            "save_load_actions_count": 0,
            "back_from_actions_count": 0,
            "enter_actions_count": 0,
            "back_from_explorer_count": 0,
            "enter_explorer_count": 0
        }
        
        # Cargar configuración de mapeo de gestos desde archivo JSON
        self.load_inputs()



    def load_inputs(self):
        """
        Cargar estructura de mapeo de gestos desde JSON y verificar estado del tutorial.
        
        Flujo de carga:
        1. Si archivo de usuario no existe:
           - Intentar copiar desde plantilla default_inputs.json
           - Si falla, crear estructura de emergencia (vital para tests)
        2. Si archivo existe:
           - Cargar JSON desde disco
        3. Verificar estado de tutorial:
           - Leer app_settings.json para onboarding_completed
           - Marcar is_first_run_session según historial
        
        Nota: Este método se ejecuta automáticamente en __init__()
        """
        # === PARTE 1: CARGAR ESTRUCTURA DE GESTOS ===
        # Si el archivo de guardado del usuario no existe (ej. primera ejecución o tests)
        if not os.path.exists(self.json_path):
            # Intentamos copiar la plantilla base si existe
            if hasattr(self, 'default_json_path') and os.path.exists(self.default_json_path):
                with open(self.default_json_path, 'r', encoding='utf-8') as df:
                    self.input_structure = json.load(df)
            else:
                # Fallback de emergencia (Vital para que los tests pasen sin dependencias)
                self.input_structure = {
                    "smile": {"category_type": "system", "function": "click", "input": "SYS_NAV_ENTER", "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthPucker": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthFunnel": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "eyeBlinkRight": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "eyeBlinkLeft": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "eyesWide": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "browDown": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "jawOpen": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthLeft": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthRight": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthPress": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "mouthShrug": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False},
                    "noseLeft": {"threshold": 0.6,"d-pad": False,"score": 0.0,"active": False},
                    "noseRight": {"threshold": 0.4,"d-pad": False,"score": 0.0,"active": False},
                    "noseUp": {"threshold": 0.4,"d-pad": False,"score": 0.0,"active": False},
                    "noseDown": {"threshold": 0.6,"d-pad": False,"score": 0.0,"active": False}
                }
            self.save_inputs()
        else:
            # === PARTE 2: CARGAR DESDE ARCHIVO EXISTENTE ===
            # Si el archivo ya existe (ejecución normal, no primera vez)
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.input_structure = json.load(f)

        # === PARTE 3: VERIFICACIÓN DE TUTORIAL ===
        # Leer estado persistente del tutorial desde app_settings.json
        onboarding_completed = False
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r') as f:
                    settings = json.load(f)
                    # Obtener estado: True si tutorial completado anteriormente
                    onboarding_completed = settings.get("onboarding_completed", False)
                    # Detectar si el desarrollador ha activado el modo test
                    self.test_mode = settings.get("test_mode", False)
            except Exception:
                # Si archivo corrupto o no legible, asumir que no fue completado
                onboarding_completed = False

        # Solo si explícitamente se completó el tutorial, dejamos de marcar primera ejecución
        # Esto permite mostrar el tutorial al usuario en su primera ejecución
        self.is_first_run_session = not onboarding_completed

    def complete_onboarding(self):
        """
        Marcar tutorial como completado y guardar estado persistente.
        Conserva el modo test y sortea el bloqueo de archivos ocultos de Windows.
        """
        self.is_first_run_session = False
        
        # 1. Preparamos los datos preservando el estado de test_mode
        settings_data = {
            "onboarding_completed": True,
            "test_mode": getattr(self, 'test_mode', False)
        }
        
        import os
        import ctypes
        
        # 2. ANTI-CRASHEO: Si el archivo existe, le quitamos el estado de "Oculto"
        # temporalmente usando el código de Windows FILE_ATTRIBUTE_NORMAL (0x80)
        if os.path.exists(self.settings_path):
            try:
                ctypes.windll.kernel32.SetFileAttributesW(self.settings_path, 0x80)
            except Exception:
                pass
                
        # 3. Ahora Windows sí nos permite escribir y sobreescribir sin dar PermissionError
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
        except Exception as e:
            print(f"Error menor al guardar ajustes: {e}")
            
        # 4. Volvemos a ocultar el archivo (Código 0x02)
        try:
            ctypes.windll.kernel32.SetFileAttributesW(self.settings_path, 0x02)
        except Exception:
            pass

    
    def save_inputs(self):
        """
        Guardar estructura actual de mapeo de gestos a archivo JSON.
        
        Persiste el contenido de self.input_structure al archivo en self.json_path.
        Se ejecuta automáticamente después de:
        - Crear nuevo perfil (save_as_profile)
        - Guardar mapeo de control (save_control_mapping)
        - Completar cambios de configuración
        """
        with open(self.json_path, 'w') as f:
            json.dump(self.input_structure, f, indent=4)

    def update_gesture_scores(self, mediapipe_gestures_dict):
        """
        Actualizar puntuaciones internas de gestos basadas en datos crudos de MediaPipe.
        
        Esta función mapea BlendShapes crudos de MediaPipe a gestos de alto nivel
        con lógica de suavizado, filtrado y combinación de valores.
        
        Args:
            mediapipe_gestures_dict: dict - BlendShapes crudos de MediaPipe
                Ejemplo: {"mouthSmileLeft": 0.85, "mouthSmileRight": 0.90, ...}
        
        Flujo de procesamiento:
        1. EXTRACCIÓN: Obtener valores crudos de MediaPipe
        2. CÁLCULO: Aplicar lógica de combinación y filtrado
           - Suavizar puntuaciones (promedios, máximos)
           - Restar interferencias (ej: pucker reduce funnel)
           - Mantener solo valores positivos (max(..., 0))
        3. ASIGNACIÓN: Actualizar input_structure con nuevos scores
        
        Gestos calculados:
        - Ojos: eyesWide, eyeBlinkRight, eyeBlinkLeft, browDown
        - Labios: smile, mouthPucker, mouthFunnel, mouthPress
        - Otros: jawOpen, mouthShrug, mouthLeft, mouthRight
        """
        if not mediapipe_gestures_dict:
            return

        # === PASO 1: EXTRACCIÓN DE VALORES BASE ===
        # Extraer valores crudos de MediaPipe y guardar en variables temporales
        base_smile = (mediapipe_gestures_dict.get("mouthSmileLeft", 0) + mediapipe_gestures_dict.get("mouthSmileRight", 0)) / 2
        base_funnel = mediapipe_gestures_dict.get("mouthFunnel", 0)
        base_pucker = mediapipe_gestures_dict.get("mouthPucker", 0)
        base_blink_l = mediapipe_gestures_dict.get("eyeBlinkLeft", 0)
        base_blink_r = mediapipe_gestures_dict.get("eyeBlinkRight", 0)
        base_shrug_lower = mediapipe_gestures_dict.get("mouthShrugLower", 0)
        
        # === PASO 2: CÁLCULO DE SCORES FINALES ===
        # Aplicar lógica de suavizado, filtrado e interferencia entre gestos
        
        # --- Gestos de Ojos (Eye Gestures) ---
        # Detectar ojos abiertos (máximo de ambos lados)
        score_eyes_wide = max(mediapipe_gestures_dict.get("eyeWideLeft", 0), mediapipe_gestures_dict.get("eyeWideRight", 0))
        # Guiño derecho: diferencia entre ojo derecho e izquierdo (si dcho. más cerrado)
        score_blink_right = max(base_blink_r - base_blink_l, 0)
        # Guiño izquierdo: diferencia entre ojo izquierdo y derecho (si izq. más cerrado)
        score_blink_left = max(base_blink_l - base_blink_r, 0)
        # Cejas fruncidas (máximo de ambos lados)
        score_brow_down = max(mediapipe_gestures_dict.get("browDownLeft", 0), mediapipe_gestures_dict.get("browDownRight", 0))

        # --- Gestos de Labios y Sonrisa (Mouth Gestures) ---
        # Sonrisa: promedio de ambos lados, reducido por encoger labios (interfere)
        score_smile = max(base_smile - base_shrug_lower, 0)
        # Morritos: presión para fruncir, reducido por boca abierta (funnel)
        score_mouth_pucker = max(base_pucker - base_funnel, 0)
        # Boca en O: valor directo sin filtrado
        score_mouth_funnel = base_funnel 
        # Apretar labios: promedio de ambos lados
        score_mouth_press = (mediapipe_gestures_dict.get("mouthPressLeft", 0) + mediapipe_gestures_dict.get("mouthPressRight", 0)) / 2

        # --- Gestos de Mandíbula y Expresión (Jaw & Expression Gestures) ---
        # Abrir boca: valor directo reducido por boca en O (funnel)
        score_jaw_open = max(mediapipe_gestures_dict.get("jawOpen", 0) - base_funnel, 0)
        # Encoger labios: complejo (reduce por pucker, funnel, press)
        score_mouth_shrug = max(base_shrug_lower - base_pucker - base_funnel - score_mouth_press, 0)
        # Mover boca a derecha: valor directo
        score_mouth_right = mediapipe_gestures_dict.get("mouthRight", 0)
        # Mover boca a izquierda: valor directo
        score_mouth_left = mediapipe_gestures_dict.get("mouthLeft", 0)
        
        # === PASO 3: ASIGNACIÓN AL MODELO ===
        # Actualizar input_structure con los scores calculados
        self.set_score("smile", score_smile)
        self.set_score("mouthPucker", score_mouth_pucker)
        self.set_score("mouthFunnel", score_mouth_funnel)
        
        self.set_score("eyeBlinkRight", score_blink_right)
        self.set_score("eyeBlinkLeft", score_blink_left)
        self.set_score("eyesWide", score_eyes_wide)
        self.set_score("browDown", score_brow_down)
        
        self.set_score("jawOpen", score_jaw_open)
        self.set_score("mouthLeft", score_mouth_left)
        self.set_score("mouthRight", score_mouth_right)

        self.set_score("mouthPress", score_mouth_press)
        self.set_score("mouthShrug", score_mouth_shrug)


    def set_score(self, gesture, value):
        """
        Establecer puntuación de un gesto en el modelo.
        
        Args:
            gesture: str - nombre del gesto (ej: "smile", "eyeBlinkLeft")
            value: float - puntuación del gesto (0.0 a 1.0)
        
        Si el gesto existe en input_structure, actualiza su campo "score".
        """
        if gesture in self.input_structure:
            self.input_structure[gesture]["score"] = value

    def get_score(self, gesture):
        """
        Obtener puntuación actual de un gesto.
        
        Args:
            gesture: str - nombre del gesto (ej: "smile", "eyeBlinkLeft")
        
        Returns:
            float - puntuación del gesto (0.0 a 1.0), o 0.0 si gesto no existe
        """
        return self.input_structure.get(gesture, {}).get("score", 0.0)
    
    def get_input_from_gesture(self, gesture):
        """
        Obtener código de entrada de mando asociado a un gesto.
        
        Args:
            gesture: str - nombre del gesto
        
        Returns:
            str - código de botón (ej: "XUSB_GAMEPAD_A"), acción de sistema (ej: "SYS_NAV_ENTER"),
                  o None si no está mapeado
        """
        return self.input_structure.get(gesture, {}).get("input", None)
    
    def get_type_from_gesture(self, gesture):
        """Devuelve el tipo de categoría ('gamepad', 'system', 'none') asociada a un gesto."""
        return self.input_structure.get(gesture, {}).get("category_type", "none")
    
    def save_control_mapping(self, gesture_code, input_code, threshold):
        """
        Actualiza el mapeo de los gestos exclusivamente en memoria RAM (no escribe en disco).
        
        Args:
            gesture_code: str - Código interno del gesto
            input_code: str - Acción o botón a mapear
            threshold: float - Sensibilidad deseada (0-100 desde la UI)
        """
        if gesture_code not in self.input_structure:
            self.input_structure[gesture_code] = {}

        # 1. El slider de la UI va de 0 a 100, pero la IA usa de 0.0 a 1.0
        self.input_structure[gesture_code]["threshold"] = threshold / 100.0
        
        # 2. Si el usuario selecciona "Ninguna" o desmarca todo
        if not input_code or input_code == "NONE":
            self.input_structure[gesture_code]["category_type"] = "none"
            self.input_structure[gesture_code]["function"] = "none"
            self.input_structure[gesture_code]["input"] = None
            
        # 3. Si el usuario asignó un botón del mando
        elif input_code.startswith("XUSB"):
            self.input_structure[gesture_code]["category_type"] = "gamepad"
            self.input_structure[gesture_code]["function"] = "pushInputButton"
            self.input_structure[gesture_code]["input"] = input_code
            
        # 4. Si el usuario asignó una acción de sistema (ej. Cambiar Modo)
        elif input_code.startswith("SYS"):
            self.input_structure[gesture_code]["category_type"] = "system"
            self.input_structure[gesture_code]["input"] = input_code
            if input_code == "SYS_CHANGE_MODE":
                self.input_structure[gesture_code]["function"] = "changeMovementMode"
            elif input_code == "SYS_RESTORE_APP":
                self.input_structure[gesture_code]["function"] = "restoreApp"
            elif input_code == "SYS_NAV_ENTER":
                self.input_structure[gesture_code]["function"] = "click"
                
    def get_available_profiles(self):
        """Devuelve una lista con los nombres de los archivos .json en la carpeta de perfiles 'controls'."""
        if not os.path.exists(self.controls_dir):
            return []
        # Filtramos solo los archivos JSON
        return [f for f in os.listdir(self.controls_dir) if f.endswith('.json')]

    def load_profile(self, filename):
        """Cambia el archivo de configuración objetivo y recarga toda la estructura en la memoria RAM."""
        self.json_path = os.path.join(self.controls_dir, filename)
        self.load_inputs()
    
    def save_as_profile(self, new_filename):
        """Crea un nuevo archivo JSON, vuelca la configuración actual y lo establece como el perfil activo."""
        # Asegurarnos de que termina en .json
        if not new_filename.lower().endswith('.json'):
            new_filename += '.json'
            
        # Actualizamos la ruta actual al nuevo archivo
        self.json_path = os.path.join(self.controls_dir, new_filename)
        
        # Llamamos al método interno para que vuelque la memoria al disco
        self.save_inputs()

    def auto_detect_steam_games(self):
        """
        Escanea la instalación local de Steam y consolida todos los perfiles de juegos detectados
        en una única base de datos JSON estructurada.
        
        Returns:
            bool - True si hubo cambios (juegos nuevos o actualizaciones), False si todo sigue igual.
        """
        import os, glob, json, winreg
        
        # 1. Buscar la ruta de instalación principal de Steam en el Registro de Windows
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
        except FileNotFoundError:
            print("Steam no está instalado.")
            return False

        # Ruta hacia la caché de biblioteca donde se esconden los iconos/logos
        steam_library_cache = os.path.join(steam_path, "appcache", "librarycache")

        # 2. Leer archivos VDF para descubrir si el usuario tiene múltiples bibliotecas en otros discos
        library_paths = []
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        
        if os.path.exists(vdf_path):
            try:
                with open(vdf_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '"path"' in line:
                            partes = line.split('"')
                            if len(partes) >= 4:
                                ruta_limpia = partes[3].replace('\\\\', '\\')
                                library_paths.append(ruta_limpia)
            except Exception:
                library_paths.append(steam_path)
        else:
            library_paths.append(steam_path)

        # --- CARGAMOS LA BASE DE DATOS ACTUAL A MEMORIA ---
        steam_data = {}
        if os.path.exists(self.steam_games_file):
            try:
                with open(self.steam_games_file, 'r', encoding='utf-8') as f:
                    steam_data = json.load(f)
            except Exception:
                steam_data = {} # Si no existe o está corrupto, empezamos de cero

        hubo_cambios = False

        # Comenzamos el escaneo iterando sobre cada biblioteca detectada
        for lib_path in library_paths:
            steamapps_path = os.path.join(lib_path, "steamapps")
            if not os.path.exists(steamapps_path):
                continue

            # Buscar los manifiestos individuales de cada juego instalado (.acf)
            for file_path in glob.glob(os.path.join(steamapps_path, "*.acf")):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Analizar el archivo para extraer ID y Nombre del juego
                    name, app_id = "", ""
                    for line in content.split('\n'):
                        if '"name"' in line:
                            name = line.split('"')[3]
                        if '"appid"' in line:
                            app_id = line.split('"')[3]

                    if name and app_id:
                        app_id = str(app_id).strip()
                        
                        # Excluir aplicaciones del sistema de Steam (e.g. Steamworks Common Redistributables)
                        if app_id in ["228980"]: # Lista negra
                            continue

                        # --- BÚSQUEDA DEL LOGO ---
                        # Buscar la mejor imagen en la caché para mostrarla en el catálogo visual
                        best_image = ""
                        app_folder = os.path.join(steam_library_cache, app_id)
                        
                        if os.path.exists(app_folder) and os.path.isdir(app_folder):
                            for root, dirs, files in os.walk(app_folder):
                                for archivo in files:
                                    if archivo.lower() == 'logo.png':
                                        best_image = os.path.join(root, archivo)
                                        break
                                if best_image: break
                            
                            # Fallback si no hay "logo.png" exacto
                            if not best_image:
                                archivos = os.listdir(app_folder)
                                imagenes = [f for f in archivos if f.lower().endswith(('.jpg', '.jpeg', '.png', '.ico'))]
                                if imagenes:
                                    imagenes.sort()
                                    best_image = os.path.join(app_folder, imagenes[0])
                            
                            if best_image:
                                best_image = best_image.replace('\\\\', '\\')

                        # Estructurar los datos unificados del juego
                        scanned_data = {
                            "title": name,
                            "exe_path": f"steam://rungameid/{app_id}",
                            "icon": best_image
                        }

                        # LÓGICA DE ACTUALIZACIÓN DEL DICCIONARIO
                        if app_id in steam_data:
                            existing = steam_data[app_id]
                            # Verificar si la ruta, icono o título han mutado desde la última vez
                            if (existing.get("exe_path") != scanned_data["exe_path"] or 
                                existing.get("icon") != scanned_data["icon"] or
                                existing.get("title") != scanned_data["title"]):
                                
                                # Actualizamos solo los datos que controlamos por si el usuario añadió campos manuales
                                steam_data[app_id].update(scanned_data)
                                hubo_cambios = True
                        else:
                            # Inserción de juego completamente nuevo
                            steam_data[app_id] = scanned_data
                            hubo_cambios = True
                            
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
                    continue

        # --- ESCRITURA FINAL ---
        if hubo_cambios:
            try:
                # Guardamos la estructura entera 1 sola vez en el JSON maestro
                with open(self.steam_games_file, 'w', encoding='utf-8') as f:
                    json.dump(steam_data, f, indent=4)
            except Exception as e:
                print(f"Error crítico al guardar steam_games.json: {e}")

        return hubo_cambios

    def get_installed_games(self):
        """Lee la BD unificada de Steam y la fusiona con la caché en tiempo real de las ROMs."""
        import json, os
        games_list = []
        
        # 1. Cargar juegos de Steam (1 sola lectura a disco)
        if os.path.exists(self.steam_games_file):
            try:
                with open(self.steam_games_file, 'r', encoding='utf-8') as f:
                    steam_data = json.load(f)
                    
                    # Extraemos los valores del diccionario a formato lista
                    for app_id, datos_juego in steam_data.items():
                        datos_juego["profile_file"] = "steam_games.json"
                        games_list.append(datos_juego)
            except Exception as e:
                print(f"Error al leer la BD de Steam: {e}")
                        
        # 2. Inyectar en memoria RAM los directorios de emuladores (las ROMs no van a archivo maestro)
        games_list.extend(self.get_dynamic_roms())
                
        return games_list
        
    def get_rom_folders(self):
        """Devuelve la lista de rutas en disco guardadas por el usuario como directorios de ROMs."""
        import json, os
        if os.path.exists(self.rom_folders_file):
            try:
                with open(self.rom_folders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def add_rom_folder(self, folder_path):
        """Añade una nueva ruta a la lista de exploración y limpia la caché para forzar un re-escaneo."""
        import json
        folders = self.get_rom_folders()
        
        # Si la ruta ya existe, la quitamos y la volvemos a poner para que pase al final de la lista
        if folder_path in folders:
            folders.remove(folder_path)
        folders.append(folder_path)
        
        with open(self.rom_folders_file, 'w', encoding='utf-8') as f:
            json.dump(folders, f, indent=4)
            
        # Al vaciar la caché, el próximo acceso a la pantalla de juegos forzará el escaneo recursivo
        self._cached_roms = None 

    def get_dynamic_roms(self):
        """Escanea las carpetas sobre la marcha en busca de extensiones válidas. Usa la caché interna si ya se escaneó antes."""
        # Si ya lo escaneamos en esta sesión, devolvemos la memoria directamente (0% latencia UI)
        if self._cached_roms is not None:
            return self._cached_roms
            
        # Extensiones asociadas a todas las consolas emuladas actualmente soportadas
        supported_extensions = (
            '.nes', '.sfc', '.smc', '.fig', 
            '.gb', '.gbc', '.gba', '.nds'
        )
        
        roms_encontradas = []
        import os
        
        # Escaneo profundo iterando sobre cada directorio configurado
        for folder in self.get_rom_folders():
            if not os.path.exists(folder):
                continue
                
            for root, dirs, files in os.walk(folder):
                for archivo in files:
                    if archivo.lower().endswith(supported_extensions):
                        rom_path = os.path.join(root, archivo)
                        titulo_limpio = os.path.splitext(archivo)[0]
                        
                        # Generamos un formato estándar compatible con las vistas y la BD de Steam
                        roms_encontradas.append({
                            "title": titulo_limpio,
                            "exe_path": rom_path,
                            "icon": "", 
                            "profile_file": "dinamico" # Etiqueta interna de control para no fusionar a .json
                        })
                        
        self._cached_roms = roms_encontradas # Guardamos el resultado en la RAM para optimizar siguientes llamadas
        return roms_encontradas
    
    def _load_emulators_config(self):
        """Carga la configuración persistente de los emuladores o crea una plantilla base por defecto si no existe."""
        
        # Lista exhaustiva de las consolas emparejadas con las extensiones de ROMs soportadas
        default_config = {
            "NES": "Default",
            "SNES": "Default",
            "Game Boy": "Default",
            "Game Boy Color": "Default",
            "Game Boy Advance": "Default",
            "Nintendo DS": "Default"
        }
        
        if os.path.exists(self.emulators_file):
            try:
                with open(self.emulators_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
                
        return default_config

    def save_emulators_config(self):
        """Vuelca la configuración actual de rutas de emuladores de la memoria RAM al disco duro."""
        import json
        with open(self.emulators_file, 'w', encoding='utf-8') as f:
            json.dump(self.emulators_config, f, indent=4)


    def get_console_from_extension(self, extension):
        """Asigna una extensión de archivo detectada (como '.nes') al nombre real de la consola correspondiente."""
        ext = extension.lower()
        
        # Mapeo basado en las extensiones de archivos de emuladores soportadas en el sistema
        mapping = {
            '.nes': 'NES',
            '.sfc': 'SNES', '.smc': 'SNES', '.fig': 'SNES',
            '.gb': 'Game Boy', '.gbc': 'Game Boy Color', '.gba': 'Game Boy Advance',
            '.nds': 'Nintendo DS'
        }
        return mapping.get(ext, None)


    def get_available_gestures_metadata(self):
        """Devuelve el catálogo maestro inmutable de gestos con sus nombres en español legibles por la UI."""
        return {
            "smile": "Sonrisa",
            "mouthPucker": "Morritos",
            "mouthFunnel": "Boca en O",
            "eyeBlinkRight": "Guiño Dcho",
            "eyeBlinkLeft": "Guiño Izq",
            "eyesWide": "Ojos Abiertos",
            "jawOpen": "Abrir Boca",
            "mouthLeft": "Boca Izq",
            "mouthRight": "Boca Dcha",
            "mouthPress": "Apretar Labios",
            "mouthShrug": "Encoger Labios",
            "browDown": "Cejas Fruncidas"
        }
    

    # === MÉTODOS DE TELEMETRÍA ===
    
    def log_telemetry(self, key):
        """Suma 1 a la métrica indicada si el modo test está activo."""
        if self.test_mode and key in self.telemetry:
            self.telemetry[key] += 1

    def set_tutorial_time(self, seconds):
        """Registra el tiempo exacto que tardó el usuario en superar el tutorial."""
        if self.test_mode:
            self.telemetry["tutorial_time_seconds"] = round(seconds, 2)

    def export_telemetry_csv(self):
        """Añade la sesión actual a un archivo CSV global al cerrar la aplicación."""
        if not self.test_mode:
            return
            
        import os
        import csv
        from datetime import datetime
            
        # 1. Usar un nombre de archivo fijo para acumular todas las sesiones de prueba
        filename = "UX_telemetry_results.csv"
        csv_path = get_save_path(filename)
        
        headers = [
            "Fecha y Hora de la Sesion", # Crucial para distinguir usuarios en un archivo único
            "Tiempo Tutorial (s)",
            "Volver (Menu Gestos)",
            "Acciones Guardar/Cargar",
            "Volver (Asignacion Boton)",
            "Entrar (Asignacion Boton)",
            "Volver (Explorador)",
            "Entrar (Explorador)"
        ]
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        row = [
            current_time,
            self.telemetry["tutorial_time_seconds"],
            self.telemetry["back_from_gestures_count"],
            self.telemetry["save_load_actions_count"],
            self.telemetry["back_from_actions_count"],
            self.telemetry["enter_actions_count"],
            self.telemetry["back_from_explorer_count"],
            self.telemetry["enter_explorer_count"]
        ]
        
        # 2. Comprobar si el archivo ya existe ANTES de abrirlo
        # Esto nos dirá si necesitamos escribir la fila de títulos o no
        file_exists = os.path.exists(csv_path)
        
        try:
            # 3. Modo 'a' (append). Esto inserta datos en la siguiente línea vacía sin borrar lo anterior.
            with open(csv_path, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';') 
                
                # Solo escribimos las cabeceras si el archivo es totalmente nuevo
                if not file_exists:
                    writer.writerow(headers)
                    
                # Escribimos los datos del usuario actual
                writer.writerow(row)
                
            print(f"📊 Datos de la sesión guardados correctamente en el registro global: {csv_path}")
        except Exception as e:
            print(f"Error crítico al guardar la telemetría del usuario: {e}")