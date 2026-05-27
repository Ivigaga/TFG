import json
import os
import sys
import winreg
import glob

def resolve_path(relative_path):
    """Gets the absolute path to the resource, for PyInstaller compatibility."""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        return os.path.join(base_path, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AppModel:
    def __init__(self, json_path="default_inputs.json"):
        self.json_path = json_path
        self.input_structure = {}
        self.is_continuous_mode = True
        self.target_fps = 60
        self.model_path = resolve_path('face_landmarker.task')
        self.controls_dir = resolve_path('controls')
        os.makedirs(self.controls_dir, exist_ok=True)
        self.games_dir = resolve_path('games')
        os.makedirs(self.games_dir, exist_ok=True)
        self.load_inputs()

    def load_inputs(self):
        """Loads the configuration from the JSON file."""
        if not os.path.exists(self.json_path):
            self.input_structure = {}
            return
            
        with open(self.json_path, 'r') as f:
            self.input_structure = json.load(f)
            
        # Ensure 'score' and 'active' keys exist for runtime
        for gesture, data in self.input_structure.items():
            if "score" not in data:
                data["score"] = 0.0
            if "active" not in data:
                data["active"] = False

    def save_inputs(self):
        """Saves current input configuration to JSON."""
        with open(self.json_path, 'w') as f:
            json.dump(self.input_structure, f, indent=4)

    def update_gesture_scores(self, mediapipe_gestures_dict):
        """Updates internal scores based on MediaPipe raw data."""
        if not mediapipe_gestures_dict:
            return

        # Map raw blendshapes to our abstract gestures
        self.set_score("eyeBrowsUp", max(mediapipe_gestures_dict.get("browOuterUpLeft", 0), 
                                         mediapipe_gestures_dict.get("browOuterUpRight", 0)))
        self.set_score("smile", (mediapipe_gestures_dict.get("mouthSmileLeft", 0) + 
                                 mediapipe_gestures_dict.get("mouthSmileRight", 0)) / 2)
        self.set_score("mouthPucker", mediapipe_gestures_dict.get("mouthPucker", 0))
        self.set_score("eyeBlinkRight", mediapipe_gestures_dict.get("eyeBlinkRight", 0))
        self.set_score("jawOpen", mediapipe_gestures_dict.get("jawOpen", 0))

    def set_score(self, gesture, value):
        if gesture in self.input_structure:
            self.input_structure[gesture]["score"] = value

    def get_score(self, gesture):
        return self.input_structure.get(gesture, {}).get("score", 0.0)

    def get_gesture_by_input(self, gamepad_input):
        """Returns the gesture associated with a gamepad button string."""
        for gesture, data in self.input_structure.items():
            if data.get("input") == gamepad_input:
                return gesture
        return None
    
    def get_input_from_gesture(self, gesture):
        """Returns the gamepad input associated with a gesture."""
        return self.input_structure.get(gesture, {}).get("input", None)
    
    def get_type_from_gesture(self, gesture):
        """Returns the category type ('gamepad', 'system', 'none') associated with a gesture."""
        return self.input_structure.get(gesture, {}).get("category_type", "none")
    
    def save_control_mapping(self, gesture_code, input_code, threshold):
        """Updates the gesture mapping in memory only (does not write to disk)."""
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
                
    def get_available_profiles(self):
        """Devuelve una lista con los nombres de los archivos .json en la carpeta controls."""
        if not os.path.exists(self.controls_dir):
            return []
        # Filtramos solo los archivos JSON
        return [f for f in os.listdir(self.controls_dir) if f.endswith('.json')]

    def load_profile(self, filename):
        """Cambia el archivo objetivo y recarga la estructura en memoria."""
        self.json_path = os.path.join(self.controls_dir, filename)
        self.load_inputs()
    
    def save_as_profile(self, new_filename):
        """Crea un nuevo archivo JSON, guarda la configuración actual y lo establece como activo."""
        # Asegurarnos de que termina en .json
        if not new_filename.lower().endswith('.json'):
            new_filename += '.json'
            
        # Actualizamos la ruta actual al nuevo archivo
        self.json_path = os.path.join(self.controls_dir, new_filename)
        
        # Llamamos al método que ya tenías para que vuelque la memoria al disco
        self.save_inputs()

    def auto_detect_steam_games(self):
        """Escanea las bibliotecas de Steam. Registra juegos nuevos y actualiza rutas/iconos de los ya existentes."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
        except FileNotFoundError:
            print("Steam no está instalado en el sistema.")
            return False

        steam_library_cache = os.path.join(steam_path, "appcache", "librarycache")

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
            except Exception as e:
                print(f"Error leyendo libraryfolders.vdf: {e}")
                library_paths.append(steam_path)
        else:
            library_paths.append(steam_path)

        # Contador de cualquier modificación (tanto nuevos como actualizaciones)
        hubo_cambios = False

        for lib_path in library_paths:
            steamapps_path = os.path.join(lib_path, "steamapps")
            if not os.path.exists(steamapps_path):
                continue

            for file_path in glob.glob(os.path.join(steamapps_path, "*.acf")):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    name = ""
                    app_id = ""
                    
                    for line in content.split('\n'):
                        if '"name"' in line:
                            name = line.split('"')[3]
                        if '"appid"' in line:
                            app_id = line.split('"')[3]

                    if name and app_id:
                        app_id = str(app_id).strip()
                        
                        # Lista negra de IDs (Steamworks, etc.)
                        ids_ignorados = ["228980"]
                        if app_id in ids_ignorados:
                            continue
                            
                        safe_filename = "".join(c for c in name if c.isalnum() or c in (' ', '_')).replace(' ', '_').lower()
                        json_path = os.path.join(self.games_dir, f"{safe_filename}.json")

                        # --- BÚSQUEDA RECURSIVA DE LOGO.PNG ---
                        best_image = ""
                        app_folder = os.path.join(steam_library_cache, str(app_id))
                        
                        if os.path.exists(app_folder) and os.path.isdir(app_folder):
                            for root, dirs, files in os.walk(app_folder):
                                for archivo in files:
                                    if archivo.lower() == 'logo.png':
                                        best_image = os.path.join(root, archivo)
                                        break
                                if best_image:
                                    break
                            
                            if not best_image:
                                archivos = os.listdir(app_folder)
                                imagenes = [f for f in archivos if f.lower().endswith(('.jpg', '.jpeg', '.png', '.ico'))]
                                if imagenes:
                                    imagenes.sort()
                                    best_image = os.path.join(app_folder, imagenes[0])
                            
                            if best_image:
                                best_image = best_image.replace('\\\\', '\\')

                        # Datos detectados en el escaneo actual
                        scanned_data = {
                            "title": name,
                            "exe_path": f"steam://rungameid/{app_id}",
                            "icon": best_image
                        }

                        guardar_fichero = False

                        # LÓGICA DE DETECCIÓN / ACTUALIZACIÓN
                        if os.path.exists(json_path):
                            # El juego ya existe: comprobamos si la ruta o el icono han cambiado
                            try:
                                with open(json_path, 'r', encoding='utf-8') as jf:
                                    existing_data = json.load(jf)
                                
                                # Si cambia el ejecutable o la ruta del icono, actualizamos
                                if (existing_data.get("exe_path") != scanned_data["exe_path"] or 
                                    existing_data.get("icon") != scanned_data["icon"]):
                                    
                                    existing_data["exe_path"] = scanned_data["exe_path"]
                                    existing_data["icon"] = scanned_data["icon"]
                                    existing_data["title"] = scanned_data["title"] # Por si cambió de nombre
                                    
                                    scanned_data = existing_data # Conservamos posibles campos extra
                                    guardar_fichero = True
                                    print(f"Actualizando ruta/icono de: {name}")
                            except Exception:
                                # Fichero corrupto: forzamos sobreescritura limpia
                                guardar_fichero = True
                        else:
                            # Juego nuevo: se crea por primera vez
                            guardar_fichero = True
                            print(f"Nuevo juego detectado: {name}")

                        # Guardamos en disco solo si es nuevo o si ha cambiado algo
                        if guardar_fichero:
                            with open(json_path, 'w', encoding='utf-8') as jf:
                                json.dump(scanned_data, jf, indent=4)
                            hubo_cambios = True
                            
                except Exception as e:
                    print(f"Error procesando el manifiesto {file_path}: {e}")
                    continue

        return hubo_cambios
    
    def get_installed_games(self):
        """Lee los archivos .json de la carpeta 'games' y devuelve una lista con sus datos."""
        games_list = []
        if not os.path.exists(self.games_dir):
            return games_list

        for archivo in os.listdir(self.games_dir):
            if archivo.endswith('.json'):
                ruta_completa = os.path.join(self.games_dir, archivo)
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        datos_juego = json.load(f)
                        # Guardamos el nombre del archivo para identificarlo si es necesario
                        datos_juego["profile_file"] = archivo
                        games_list.append(datos_juego)
                except Exception as e:
                    print(f"Error al leer el juego {archivo}: {e}")
                    
        return games_list