import json
import os
import sys

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