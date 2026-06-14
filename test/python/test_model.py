import pytest
import os
import json
from unittest.mock import patch
from model import AppModel

@pytest.fixture
def temp_model(tmp_path):
    """
    Crea una instancia de AppModel totalmente aislada.
    Cualquier intento de leer o guardar datos será redirigido a la carpeta temporal de Pytest.
    """
    # 1. Crear estructura de carpetas mínima obligatoria
    os.makedirs(tmp_path / "controls", exist_ok=True)
    os.makedirs(tmp_path / "games", exist_ok=True)
    
    # 2. Secuestramos la función de rutas del modelo
    def mock_save_path(relative_path):
        return str(tmp_path / relative_path)
        
    with patch('model.get_save_path', side_effect=mock_save_path):
        # Al nacer bajo el parche, TODO el modelo apunta al entorno virtual
        model = AppModel(json_path="controls/test_inputs.json")
        model.is_first_run_session = True 
        return model

@pytest.fixture
def dirty_model(tmp_path):
    """Crea un AppModel precargado con datos sucios simulados, totalmente aislado."""
    os.makedirs(tmp_path / "controls", exist_ok=True)
    dirty_json_path = tmp_path / "controls" / "dirty_inputs.json"
    
    dirty_data = {
        "mouthPucker": {
            "category_type": "system", "function": "click", "input": "SYS_NAV_ENTER",
            "threshold": 0.7, "active": True, "score": 0.95
        },
        "eyeBlinkRight":{
            "category_type": "gamepad", "function": "pressInputButton", "input": "XUSB_GAMEPAD_B",
            "threshold": 0.6, "active": True, "score": 0.8
        },
        "smile":{
            "category_type": "none", "function": "none", "input": None,
            "threshold": 0.5, "active": True, "score": 0.9          
        }
    }
    
    with open(dirty_json_path, 'w', encoding='utf-8') as f:
        json.dump(dirty_data, f)
        
    def mock_save_path(relative_path):
        return str(tmp_path / relative_path)
        
    with patch('model.get_save_path', side_effect=mock_save_path):
        return AppModel(json_path="controls/dirty_inputs.json")

def test_get_console_from_extension(temp_model):
    """Verifies that ROM extensions map correctly to console names."""
    assert temp_model.get_console_from_extension(".nes") == "NES"
    assert temp_model.get_console_from_extension(".gba") == "Game Boy Advance"
    assert temp_model.get_console_from_extension(".unknown") is None

def test_save_control_mapping_gamepad(temp_model):
    """Verifies that gesture settings are correctly formatted and saved in memory."""
    temp_model.save_control_mapping("smile", "XUSB_GAMEPAD_A", 75)
    
    assert temp_model.input_structure["smile"]["threshold"] == 0.75
    assert temp_model.input_structure["smile"]["category_type"] == "gamepad"
    assert temp_model.input_structure["smile"]["input"] == "XUSB_GAMEPAD_A"
    assert temp_model.input_structure["smile"]["function"] == "pushInputButton"

def test_save_control_mapping_system(temp_model):
    """Verifies that system actions are correctly saved in memory."""
    temp_model.save_control_mapping("jawOpen", "SYS_RESTORE_APP", 60)
    assert temp_model.input_structure["jawOpen"]["threshold"] == 0.6
    assert temp_model.input_structure["jawOpen"]["category_type"] == "system"
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_RESTORE_APP"
    assert temp_model.input_structure["jawOpen"]["function"] == "restoreApp"

    temp_model.save_control_mapping("jawOpen", "SYS_CHANGE_MODE", 60)
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_CHANGE_MODE"

    temp_model.save_control_mapping("jawOpen", "SYS_NAV_ENTER", 60)
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_NAV_ENTER"

def test_save_control_mapping_none(temp_model):
    """Verifies that clearing a gesture resets its properties safely."""
    temp_model.save_control_mapping("jawOpen", "NONE", 50)
    assert temp_model.input_structure["jawOpen"]["category_type"] == "none"
    assert temp_model.input_structure["jawOpen"]["input"] is None

@patch('model.get_save_path')
def test_load_inputs_creates_emergency_fallback(mock_save_path, tmp_path):
    """Escenario C: Falla todo. El diccionario se crea de cero."""
    os.makedirs(tmp_path / "controls", exist_ok=True)
    os.makedirs(tmp_path / "games", exist_ok=True)
    
    # Engañamos a las rutas. Como tmp_path está vacío, no encontrará la plantilla real
    mock_save_path.side_effect = lambda p: str(tmp_path / p)
        
    model = AppModel(json_path="controls/does_not_exist.json")
        
    assert "smile" in model.input_structure
    assert model.input_structure["smile"]["category_type"] == "system"
    assert model.input_structure["noseLeft"]["threshold"] == 0.6
    
    assert os.path.exists(str(tmp_path / "controls" / "does_not_exist.json"))

@patch('model.get_save_path')
def test_load_inputs_copies_template_on_first_run(mock_save_path, tmp_path):
    """Escenario B: Primera ejecución normal clonando la plantilla falsa."""
    os.makedirs(tmp_path / "controls", exist_ok=True)
    os.makedirs(tmp_path / "games", exist_ok=True)
    
    fake_template_file = tmp_path / "controls" / "default_inputs.json"
    fake_user_file = tmp_path / "controls" / "first_run.json"
    
    plantilla_limpia = {
        "smile": {"category_type": "system", "function": "click", "input": "SYS_NAV_ENTER", "threshold": 0.5, "score": 0.0, "active": False},
        "mouthPucker": {"category_type": "none", "function": "none", "input": None, "threshold": 0.5, "score": 0.0, "active": False}
    }
    
    with open(fake_template_file, 'w', encoding='utf-8') as f:
        json.dump(plantilla_limpia, f)
        
    mock_save_path.side_effect = lambda p: str(tmp_path / p)
    
    model = AppModel(json_path="controls/first_run.json")
    
    assert model.input_structure["mouthPucker"]["score"] == 0.0
    assert os.path.exists(str(fake_user_file))

def test_update_gesture_score_logic(temp_model):
    """Verifica que el modelo registra correctamente las nuevas puntuaciones de los gestos."""
    assert temp_model.input_structure["smile"]["score"] == 0.0
    temp_model.input_structure["smile"]["score"] = 0.85
    assert temp_model.input_structure["smile"]["score"] == 0.85

def test_get_information_from_gesture(dirty_model):
    """Verifies that we can retrieve the input code associated with a gesture."""
    model = dirty_model
    assert model.get_input_from_gesture("mouthPucker") == "SYS_NAV_ENTER"
    assert model.get_input_from_gesture("eyeBlinkRight") == "XUSB_GAMEPAD_B"
    assert model.get_type_from_gesture("mouthPucker") == "system"

def test_dynamic_rom_scanner_filters_extensions(temp_model, tmp_path):
    """Verifies that the dynamic scanner finds valid extensions without writing JSONs."""
    rom_dir = tmp_path / "my_roms"
    rom_dir.mkdir()
    
    (rom_dir / "super_mario.nes").touch()
    (rom_dir / "pokemon.gba").touch() 
    (rom_dir / "readme.txt").touch() 
    
    temp_model.add_rom_folder(str(rom_dir))
    dynamic_roms = temp_model.get_dynamic_roms()
    
    assert len(dynamic_roms) == 2
    titles = [rom["title"] for rom in dynamic_roms]
    assert "pokemon" in titles
    assert "super_mario" in titles
    assert "readme" not in titles
    assert dynamic_roms[0]["profile_file"] == "dinamico"
    
    # Confirmar que no escribió archivos individuales
    if os.path.exists(temp_model.games_dir):
        generated_files = os.listdir(temp_model.games_dir)
        assert not any("mario" in f.lower() for f in generated_files)

@patch("winreg.OpenKey", side_effect=FileNotFoundError)
def test_steam_scanner_not_installed(mock_open_key, temp_model):
    """Verifies that the scanner returns False and doesn't crash if Steam is missing."""
    assert temp_model.auto_detect_steam_games() is False

@patch("winreg.OpenKey")
@patch("winreg.CloseKey")
@patch("winreg.QueryValueEx")
def test_steam_scanner_finds_game(mock_query, mock_close_key, mock_open_key, temp_model, tmp_path):
    """Verifies that parsing a valid .acf file successfully adds the game."""
    fake_steam_dir = tmp_path / "FakeSteam"
    fake_steamapps = fake_steam_dir / "steamapps"
    fake_steamapps.mkdir(parents=True)
    
    # FIX: Replicamos el formato multilinea exacto de los archivos .acf de Steam
    fake_acf_content = '{"AppState": {\n"appid"\t\t"123"\n"name"\t\t"Fake Test Game"\n}}'
    
    acf_file = fake_steamapps / "appmanifest_123.acf"
    acf_file.write_text(fake_acf_content, encoding='utf-8')
    
    mock_query.return_value = (str(fake_steam_dir), 1)
    
    changed = temp_model.auto_detect_steam_games()
    assert changed is True
    
    games = temp_model.get_installed_games()
    assert any(g.get("title") == "Fake Test Game" for g in games)

def test_profile_management_flow(temp_model):
    """Verifies creating, listing, and loading custom JSON profiles."""
    temp_model.save_control_mapping("jawOpen", "XUSB_GAMEPAD_A", 80)
    temp_model.save_as_profile("action_game_profile")
    
    profiles = temp_model.get_available_profiles()
    assert "action_game_profile.json" in profiles
    
    temp_model.save_control_mapping("jawOpen", "NONE", 50)
    temp_model.load_profile("action_game_profile.json")
    
    assert temp_model.input_structure["jawOpen"]["input"] == "XUSB_GAMEPAD_A"

@patch('model.get_save_path')
def test_emulator_configuration_persistence(mock_save_path, temp_model, tmp_path):
    """Verifies that custom emulator paths survive a simulated restart."""
    # Obligamos a que el reinicio también esté enjaulado
    mock_save_path.side_effect = lambda p: str(tmp_path / p)
    
    fake_exe_path = os.path.join("C:", "Emulators", "fceux.exe")
    temp_model.emulators_config["NES"] = fake_exe_path
    temp_model.save_emulators_config()
    
    # Reinicio del programa simulado
    new_model = AppModel(json_path="controls/test_inputs.json")
    reloaded_config = new_model._load_emulators_config()
    
    assert reloaded_config["NES"] == fake_exe_path
    assert reloaded_config["SNES"] == "Default"

def test_get_installed_games_merges_steam_and_roms(temp_model, tmp_path):
    """Verifies that get_installed_games successfully combines all sources."""
    steam_data = {
        "999": {"title": "Fake Steam Game", "exe_path": "steam://rungameid/999", "icon": ""}
    }
    with open(temp_model.steam_games_file, 'w', encoding='utf-8') as f:
        json.dump(steam_data, f)
        
    rom_dir = tmp_path / "my_roms"
    rom_dir.mkdir()
    (rom_dir / "sonic.sfc").touch()
    temp_model.add_rom_folder(str(rom_dir))
    
    all_games = temp_model.get_installed_games()
    
    assert len(all_games) == 2
    assert next(g for g in all_games if g["title"] == "Fake Steam Game")["profile_file"] == "steam_games.json"
    assert next(g for g in all_games if g["title"] == "sonic")["profile_file"] == "dinamico"

def test_complete_onboarding_creates_settings_file(temp_model):
    """Verifica que al completar el tutorial se guarda el estado globalmente en app_settings.json."""
    assert temp_model.is_first_run_session is True
    temp_model.complete_onboarding()
    assert temp_model.is_first_run_session is False
    assert os.path.exists(temp_model.settings_path)