import json
import os
import sys
import winreg
import glob

def get_asset_path(relative_path):
    """Usar SOLO para archivos de lectura que vienen empaquetados (IA, estilos, iconos fijos)."""
    if getattr(sys, 'frozen', False):
        # sys._MEIPASS apunta directamente a la carpeta _internal de PyInstaller
        base_path = sys._MEIPASS
    else:
        # En desarrollo, subimos un nivel desde /src y entramos en /conf
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))
    return os.path.join(base_path, relative_path)

def get_save_path(relative_path):
    """Usar SOLO para archivos de escritura/usuario (JSONs, portadas descargadas)."""
    if getattr(sys, 'frozen', False):
        # sys.executable apunta a la raíz donde está el .exe, ideal para guardar datos
        base_path = os.path.dirname(sys.executable)
    else:
        # En desarrollo, subimos un nivel desde /src y entramos en /conf
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'conf'))
    return os.path.join(base_path, relative_path)

class AppModel:
    def __init__(self, json_path="controls/default_inputs.json"):
        self.json_path = get_asset_path(json_path)
        self.default_json_path = get_asset_path("controls/default_inputs.json")
        self.input_structure = {}
        self.is_continuous_mode = True
        self.target_fps = 60
        self.model_path = get_asset_path('face_landmarker.task')
        self.controls_dir = get_save_path('controls')
        os.makedirs(self.controls_dir, exist_ok=True)
        self.games_dir = get_save_path('games')
        os.makedirs(self.games_dir, exist_ok=True)
        
        self.rom_folders_file = get_save_path('games/rom_folders.json') 
        self.steam_games_file = get_save_path('games/steam_games.json')
        
        self.emulators_file = get_save_path('games/emulators.json')
        self.emulators_config = self._load_emulators_config()
        
        self._cached_roms = None
        
        os.makedirs(self.games_dir, exist_ok=True)


        self.load_inputs()



    def load_inputs(self):
        """Loads the configuration from the JSON file."""
        if not os.path.exists(self.json_path):
            self.input_structure = {
                "jawOpen": {"category_type": "none","function": "none", "input": None, "threshold": 0.5},
                "eyeBlinkRight": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5},
                "eyeBrowsUp": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5},
                "mouthPucker": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5},
                "smile": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5},
                "noseLeft": {"threshold": 0.6,"d-pad": False,"score": 0.0,"active": False},
                "noseRight": {"threshold": 0.4,"d-pad": False,"score": 0.0,"active": False},
                "noseUp": {"threshold": 0.4,"d-pad": False,"score": 0.0,"active": False},
                "noseDown": {"threshold": 0.6,"d-pad": False,"score": 0.0,"active": False}
                }
            self.json_path =self.default_json_path
            self.save_inputs()  # Guardamos el JSON por primera vez con la estructura por defecto
            for gesture, data in self.input_structure.items():
                data["score"] = 0.0
                data["active"] = False
            return
            
        with open(self.json_path, 'r') as f:
            self.input_structure = json.load(f)
            
        # Ensure 'score' and 'active' keys exist for runtime
        for gesture, data in self.input_structure.items():
            data["score"] = 0.0
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
            elif input_code == "SYS_RESTORE_APP":
                self.input_structure[gesture_code]["function"] = "restoreApp"
            elif input_code == "SYS_NAV_ENTER":
                self.input_structure[gesture_code]["function"] = "click"
                
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
        """Escanea Steam y consolida todos los perfiles en una única base de datos JSON."""
        import os, glob, json, winreg
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")
            steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
        except FileNotFoundError:
            print("Steam no está instalado.")
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

        # Comenzamos el escaneo
        for lib_path in library_paths:
            steamapps_path = os.path.join(lib_path, "steamapps")
            if not os.path.exists(steamapps_path):
                continue

            for file_path in glob.glob(os.path.join(steamapps_path, "*.acf")):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    name, app_id = "", ""
                    for line in content.split('\n'):
                        if '"name"' in line:
                            name = line.split('"')[3]
                        if '"appid"' in line:
                            app_id = line.split('"')[3]

                    if name and app_id:
                        app_id = str(app_id).strip()
                        
                        if app_id in ["228980"]: # Lista negra
                            continue

                        # --- BÚSQUEDA DEL LOGO ---
                        best_image = ""
                        app_folder = os.path.join(steam_library_cache, app_id)
                        
                        if os.path.exists(app_folder) and os.path.isdir(app_folder):
                            for root, dirs, files in os.walk(app_folder):
                                for archivo in files:
                                    if archivo.lower() == 'logo.png':
                                        best_image = os.path.join(root, archivo)
                                        break
                                if best_image: break
                            
                            if not best_image:
                                archivos = os.listdir(app_folder)
                                imagenes = [f for f in archivos if f.lower().endswith(('.jpg', '.jpeg', '.png', '.ico'))]
                                if imagenes:
                                    imagenes.sort()
                                    best_image = os.path.join(app_folder, imagenes[0])
                            
                            if best_image:
                                best_image = best_image.replace('\\\\', '\\')

                        # Datos estructurados
                        scanned_data = {
                            "title": name,
                            "exe_path": f"steam://rungameid/{app_id}",
                            "icon": best_image
                        }

                        # LÓGICA DE ACTUALIZACIÓN DEL DICCIONARIO
                        if app_id in steam_data:
                            existing = steam_data[app_id]
                            if (existing.get("exe_path") != scanned_data["exe_path"] or 
                                existing.get("icon") != scanned_data["icon"] or
                                existing.get("title") != scanned_data["title"]):
                                
                                # Actualizamos solo los datos que controlamos por si el usuario añadió campos manuales
                                steam_data[app_id].update(scanned_data)
                                hubo_cambios = True
                        else:
                            # Inserción de juego nuevo
                            steam_data[app_id] = scanned_data
                            hubo_cambios = True
                            
                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")
                    continue

        # --- ESCRITURA FINAL ---
        if hubo_cambios:
            try:
                # Guardamos la estructura entera 1 sola vez
                with open(self.steam_games_file, 'w', encoding='utf-8') as f:
                    json.dump(steam_data, f, indent=4)
            except Exception as e:
                print(f"Error crítico al guardar steam_games.json: {e}")

        return hubo_cambios

    def get_installed_games(self):
        """Lee la BD unificada de Steam y la fusiona con la caché de ROMs."""
        import json, os
        games_list = []
        
        # 1. Cargar juegos de Steam (1 sola lectura a disco)
        if os.path.exists(self.steam_games_file):
            try:
                with open(self.steam_games_file, 'r', encoding='utf-8') as f:
                    steam_data = json.load(f)
                    
                    # Extraemos los valores del diccionario
                    for app_id, datos_juego in steam_data.items():
                        datos_juego["profile_file"] = "steam_games.json"
                        games_list.append(datos_juego)
            except Exception as e:
                print(f"Error al leer la BD de Steam: {e}")
                        
        # 2. Inyectar la memoria RAM de los emuladores
        games_list.extend(self.get_dynamic_roms())
                
        return games_list
        
    def get_rom_folders(self):
        """Devuelve la lista de rutas guardadas por el usuario."""
        import json, os
        if os.path.exists(self.rom_folders_file):
            try:
                with open(self.rom_folders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def add_rom_folder(self, folder_path):
        """Añade una ruta a la configuración y limpia la caché para forzar un re-escaneo."""
        import json
        folders = self.get_rom_folders()
        
        # Si la ruta ya existe, la quitamos y la volvemos a poner para que pase al final de la lista
        if folder_path in folders:
            folders.remove(folder_path)
        folders.append(folder_path)
        
        with open(self.rom_folders_file, 'w', encoding='utf-8') as f:
            json.dump(folders, f, indent=4)
            
        # Al vaciar la caché, el próximo acceso a la pantalla de juegos forzará el escaneo
        self._cached_roms = None 

    def get_dynamic_roms(self):
        """Escanea las carpetas sobre la marcha. Usa la caché si ya se escaneó antes."""
        # Si ya lo escaneamos en esta sesión, devolvemos la memoria directamente (0% latencia)
        if self._cached_roms is not None:
            return self._cached_roms
            
        supported_extensions = (
            '.nes', '.sfc', '.smc', '.fig', 
            '.gb', '.gbc', '.gba', '.nds'
        )
        
        roms_encontradas = []
        import os
        
        for folder in self.get_rom_folders():
            if not os.path.exists(folder):
                continue
                
            for root, dirs, files in os.walk(folder):
                for archivo in files:
                    if archivo.lower().endswith(supported_extensions):
                        rom_path = os.path.join(root, archivo)
                        titulo_limpio = os.path.splitext(archivo)[0]
                        
                        roms_encontradas.append({
                            "title": titulo_limpio,
                            "exe_path": rom_path,
                            "icon": "", 
                            "profile_file": "dinamico" # Etiqueta interna de control
                        })
                        
        self._cached_roms = roms_encontradas # Guardamos el resultado en la RAM
        return roms_encontradas
    
    def _load_emulators_config(self):
        """Loads emulator configuration or creates a default one."""
        
        # Comprehensive list of consoles mapped to supported ROM extensions
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
        """Saves current emulator configuration to disk."""
        import json
        with open(self.emulators_file, 'w', encoding='utf-8') as f:
            json.dump(self.emulators_config, f, indent=4)


    def get_console_from_extension(self, extension):
        """Maps a file extension (like '.nes') to the corresponding console name."""
        ext = extension.lower()
        
        # Mapping based on your supported extensions
        mapping = {
            '.nes': 'NES',
            '.sfc': 'SNES', '.smc': 'SNES', '.fig': 'SNES',
            '.gb': 'Game Boy', '.gbc': 'Game Boy Color', '.gba': 'Game Boy Advance',
            '.nds': 'Nintendo DS'
        }
        return mapping.get(ext, None)


