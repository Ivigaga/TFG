import pytest
import os
from model import AppModel
import json
from unittest.mock import patch, mock_open

@pytest.fixture
def temp_model(tmp_path):
    """Creates a fresh AppModel instance pointing to temporary files to avoid touching real user data."""
    import os
    
    # Base control mapping file
    temp_json = tmp_path / "test_inputs.json"
    model = AppModel(json_path=str(temp_json))
    
    # --- FIX: Redirect ALL persistent storage to the temporary test folder ---
    model.controls_dir = str(tmp_path / "controls")
    os.makedirs(model.controls_dir, exist_ok=True)
    
    model.rom_folders_file = str(tmp_path / "rom_folders.json")
    model.steam_games_file = str(tmp_path / "steam_games.json")
    model.emulators_file = str(tmp_path / "emulators.json")
    
    # Redirect the dynamic games cache directory if your model uses one
    model.games_dir = str(tmp_path / "games")
    os.makedirs(model.games_dir, exist_ok=True)
    
    return model

@pytest.fixture
def dirty_model(tmp_path):
    """Creates an AppModel pre-loaded with simulated 'dirty' leftover data."""
    dirty_json_path = tmp_path / "dirty_inputs.json"
    
    dirty_data = {
        "mouthPucker": {
            "category_type": "system",
            "function": "click",
            "input": "SYS_NAV_ENTER",
            "threshold": 0.7,
            "active": True,       # Leftover active state
            "score": 0.95         # Leftover high score
        },
        "eyeBlinkRight":{
            "category_type": "gamepad",
            "function": "pressInputButton",
            "input": "XUSB_GAMEPAD_B",
            "threshold": 0.6,
            "active": True,       # Leftover active state
            "score": 0.8          # Leftover high score
        },
        "smile":{
            "category_type": "none",
            "function": "none",
            "input": None,
            "threshold": 0.5,
            "active": True,       # Leftover active state
            "score": 0.9          # Leftover high score            
        }
    }
    
    import json
    with open(dirty_json_path, 'w') as f:
        json.dump(dirty_data, f)
        
    return AppModel(json_path=str(dirty_json_path))

def test_get_console_from_extension(temp_model):
    """Verifies that ROM extensions map correctly to console names."""
    assert temp_model.get_console_from_extension(".nes") == "NES"
    assert temp_model.get_console_from_extension(".nsp") == "Nintendo Switch"
    assert temp_model.get_console_from_extension(".iso") == "PlayStation 2"
    
    # Testing an unknown extension
    assert temp_model.get_console_from_extension(".unknown") is None

def test_save_control_mapping_gamepad(temp_model):
    """Verifies that gesture settings are correctly formatted and saved in memory."""
    # Simulating the user setting the "Smile" gesture to press 'A' with a 75% slider
    temp_model.save_control_mapping(
        gesture_code="smile", 
        input_code="XUSB_GAMEPAD_A", 
        threshold=75
    )
    
    # The UI sends 75, but the AI needs 0.75
    assert temp_model.input_structure["smile"]["threshold"] == 0.75
    assert temp_model.input_structure["smile"]["category_type"] == "gamepad"
    assert temp_model.input_structure["smile"]["input"] == "XUSB_GAMEPAD_A"
    assert temp_model.input_structure["smile"]["function"] == "pushInputButton"

def test_save_control_mapping_system(temp_model):
    """Verifies that system actions are correctly saved in memory."""
    # Simulating the user setting the "Jaw Open" gesture to trigger SYS_RESTORE_APP with a 60% slider
    temp_model.save_control_mapping(
        gesture_code="jawOpen", 
        input_code="SYS_RESTORE_APP", 
        threshold=60
    )
    
    assert temp_model.input_structure["jawOpen"]["threshold"] == 0.6
    assert temp_model.input_structure["jawOpen"]["category_type"] == "system"
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_RESTORE_APP"
    assert temp_model.input_structure["jawOpen"]["function"] == "restoreApp"

    temp_model.save_control_mapping(
        gesture_code="jawOpen", 
        input_code="SYS_CHANGE_MODE", 
        threshold=60
    )
    
    assert temp_model.input_structure["jawOpen"]["threshold"] == 0.6
    assert temp_model.input_structure["jawOpen"]["category_type"] == "system"
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_CHANGE_MODE"
    assert temp_model.input_structure["jawOpen"]["function"] == "changeMovementMode"


    temp_model.save_control_mapping(
        gesture_code="jawOpen", 
        input_code="SYS_NAV_ENTER", 
        threshold=60
    )
    
    assert temp_model.input_structure["jawOpen"]["threshold"] == 0.6
    assert temp_model.input_structure["jawOpen"]["category_type"] == "system"
    assert temp_model.input_structure["jawOpen"]["input"] == "SYS_NAV_ENTER"
    assert temp_model.input_structure["jawOpen"]["function"] == "click"

def test_save_control_mapping_none(temp_model):
    """Verifies that clearing a gesture resets its properties safely."""
    temp_model.save_control_mapping("jawOpen", "NONE", 50)
    
    assert temp_model.input_structure["jawOpen"]["category_type"] == "none"
    assert temp_model.input_structure["jawOpen"]["input"] is None

def test_load_inputs_creates_default_when_missing(tmp_path):
    """Verifies that if the JSON is missing, it loads the default structure and resets states."""
    missing_json_path = tmp_path / "does_not_exist.json"
    
    # Instantiating the model automatically calls load_inputs()
    model = AppModel(json_path=str(missing_json_path))
    
    # 1. Verify it populated the default keys
    assert "jawOpen" in model.input_structure
    assert "eyeBlinkRight" in model.input_structure
    assert "eyeBrowsUp" in model.input_structure
    assert "mouthPucker" in model.input_structure
    assert "smile" in model.input_structure
    assert "noseLeft" in model.input_structure
    assert "noseRight" in model.input_structure
    assert "noseUp" in model.input_structure
    assert "noseDown" in model.input_structure

    assert model.input_structure["jawOpen"]["input"] is None
    assert model.input_structure["eyeBlinkRight"]["input"] is None
    assert model.input_structure["eyeBrowsUp"]["input"] is None
    assert model.input_structure["mouthPucker"]["input"] is None
    assert model.input_structure["smile"]["input"] is None

    assert model.input_structure["jawOpen"]["threshold"] == 0.5
    assert model.input_structure["eyeBlinkRight"]["threshold"] == 0.5
    assert model.input_structure["eyeBrowsUp"]["threshold"] == 0.5
    assert model.input_structure["mouthPucker"]["threshold"] == 0.5
    assert model.input_structure["smile"]["threshold"] == 0.5

    assert model.input_structure["noseLeft"]["threshold"] == 0.6
    assert model.input_structure["noseRight"]["threshold"] == 0.4
    assert model.input_structure["noseUp"]["threshold"] == 0.4
    assert model.input_structure["noseDown"]["threshold"] == 0.6

    
    # 2. Verify that runtime states were securely initialized to zero/false
    assert model.input_structure["jawOpen"]["score"] == 0.0
    assert model.input_structure["noseUp"]["active"] is False

def test_load_inputs_resets_dirty_state(tmp_path):
    """Verifies that loading an existing file wipes 'score' and 'active' to prevent ghost clicks."""
    dirty_json_path = tmp_path / "dirty_inputs.json"
    
    # Create a "dirty" save file simulating a leftover from a previous session
    dirty_data = {
        "mouthPucker": {
            "category_type": "system",
            "function": "click",
            "input": "SYS_NAV_ENTER",
            "threshold": 0.7,
            "active": True,       # Leftover active state
            "score": 0.95         # Leftover high score
        }
    }
    
    with open(dirty_json_path, 'w') as f:
        json.dump(dirty_data, f)
        
    # Load the model with this specific dirty file
    model = AppModel(json_path=str(dirty_json_path))
    
    # The structure and settings should be loaded...
    assert "mouthPucker" in model.input_structure
    assert model.input_structure["mouthPucker"]["function"] == "click"
    assert model.input_structure["mouthPucker"]["threshold"] == 0.7
    assert model.input_structure["mouthPucker"]["input"] == "SYS_NAV_ENTER"
        
    # ...but the runtime states MUST be wiped clean to zero/false
    assert model.input_structure["mouthPucker"]["score"] == 0.0 
    assert model.input_structure["mouthPucker"]["active"] is False

def test_update_gesture_score(dirty_model):
    """Verifies that updating a gesture's score correctly modifies the model's state."""
    # The dirty_model fixture provides an AppModel with simulated 'dirty' leftover data
    model = dirty_model

   
    # The structure and settings should be loaded...
    assert "mouthPucker" in model.input_structure
    assert model.input_structure["mouthPucker"]["score"] == 0.0 

    model.update_gesture_scores({"mouthPucker": 0.85})
    assert model.input_structure["mouthPucker"]["score"] == 0.85

def test_get_information_from_gesture(dirty_model):
    """Verifies that we can retrieve the input code associated with a gesture."""
    model = dirty_model
    
    # The dirty_model fixture provides an AppModel with simulated 'dirty' leftover data
    assert model.get_input_from_gesture("mouthPucker") == "SYS_NAV_ENTER"
    assert model.get_input_from_gesture("eyeBlinkRight") == "XUSB_GAMEPAD_B"
    assert model.get_input_from_gesture("smile") is None

    assert model.get_type_from_gesture("mouthPucker") == "system"
    assert model.get_type_from_gesture("eyeBlinkRight") == "gamepad"
    assert model.get_type_from_gesture("smile") == "none"

# --- ROM SCANNER TESTS ---

# --- ROM SCANNER TESTS ---

def test_dynamic_rom_scanner_filters_extensions(temp_model, tmp_path):
    """Verifies that the dynamic scanner finds valid extensions, ignores others, and stores them in RAM without writing JSONs."""
    import os
    
    # 1. Create a fake ROM folder
    rom_dir = tmp_path / "my_roms"
    rom_dir.mkdir()
    
    # Create valid ROMs and invalid files
    (rom_dir / "super_mario.nes").touch()
    (rom_dir / "zelda_ocarina.z64").touch()
    (rom_dir / "readme.txt").touch() # This should be ignored
    
    # 2. Add the folder to the model
    temp_model.add_rom_folder(str(rom_dir))
    
    # 3. Run the dynamic scanner
    dynamic_roms = temp_model.get_dynamic_roms()
    
    # 4. Assertions - Verify it found exactly the 2 valid games
    assert len(dynamic_roms) == 2
    
    # Extract titles to verify correct parsing
    titles = [rom["title"] for rom in dynamic_roms]
    assert "super_mario" in titles
    assert "zelda_ocarina" in titles
    assert "readme" not in titles
    
    # 5. Verify the internal RAM tag is applied
    assert dynamic_roms[0]["profile_file"] == "dinamico"
    assert dynamic_roms[1]["profile_file"] == "dinamico"
    
    # 6. CRITICAL: Verify NO individual JSON files were written to the games directory
    if os.path.exists(temp_model.games_dir):
        generated_files = os.listdir(temp_model.games_dir)
        # Ensure no file resembling a ROM profile was created
        assert not any("mario" in f.lower() or "zelda" in f.lower() for f in generated_files)


# --- STEAM SCANNER TESTS ---

@patch("winreg.OpenKey", side_effect=FileNotFoundError)
def test_steam_scanner_not_installed(mock_open_key, temp_model):
    """Verifies that the scanner returns False and doesn't crash if Steam is not in the registry."""
    # The @patch forces winreg to simulate that Steam is not installed
    result = temp_model.auto_detect_steam_games()
    
    assert result is False

@patch("winreg.OpenKey")
@patch("winreg.CloseKey")
@patch("winreg.QueryValueEx")
def test_steam_scanner_finds_game(mock_query, mock_close_key, mock_open_key, temp_model, tmp_path):
    """Verifies that parsing a valid .acf file successfully adds the game to the unified database."""
        
    # 1. Create a REAL temporary directory mimicking Steam's exact folder structure
    fake_steam_dir = tmp_path / "FakeSteam"
    fake_steamapps = fake_steam_dir / "steamapps"
    fake_steamapps.mkdir(parents=True)
    
    # 2. Write a real .acf file to our temporary hard drive
    fake_acf_content = '''
    "AppState"
    {
        "appid" "123"
        "name" "Fake Test Game"
    }
    '''
    acf_file = fake_steamapps / "appmanifest_123.acf"
    acf_file.write_text(fake_acf_content, encoding='utf-8')
    
    # 3. Fake the Windows Registry to point to our temporary folder
    mock_query.return_value = (str(fake_steam_dir), 1)
    
    # 4. Run the scanner
    changed = temp_model.auto_detect_steam_games()
    
    assert changed is True
    
    # 5. Check if the game was added to the unified catalog list
    games = temp_model.get_installed_games()
    
    game_found = any(
        g.get("title") == "Fake Test Game" and g.get("exe_path") == "steam://rungameid/123" 
        for g in games
    )
    assert game_found is True


# --- PROFILE MANAGEMENT TESTS ---

def test_profile_management_flow(temp_model):
    """Verifies creating, listing, and loading custom JSON profiles."""
    # 1. Modify the current model state
    temp_model.save_control_mapping("jawOpen", "XUSB_GAMEPAD_A", 80)
    
    # 2. Save as a new profile
    temp_model.save_as_profile("action_game_profile")
    
    # Verify the extension was automatically added and it appears in the list
    profiles = temp_model.get_available_profiles()
    assert "action_game_profile.json" in profiles
    
    # 3. Change the state again to something else
    temp_model.save_control_mapping("jawOpen", "NONE", 50)
    assert temp_model.input_structure["jawOpen"]["input"] is None
    
    # 4. Load the custom profile back
    temp_model.load_profile("action_game_profile.json")
    
    # Verify the state reverted to what was saved in the profile
    assert temp_model.input_structure["jawOpen"]["input"] == "XUSB_GAMEPAD_A"
    assert temp_model.input_structure["jawOpen"]["threshold"] == 0.8


# --- EMULATOR CONFIGURATION TESTS ---

def test_emulator_configuration_persistence(temp_model, tmp_path):
    """Verifies that custom emulator paths are saved and loaded correctly."""
    # 1. By default, it should be "Default"
    assert temp_model.emulators_config["NES"] == "Default"
    
    # 2. Change the path and save
    fake_exe_path = "C:\\Emulators\\fceux.exe"
    temp_model.emulators_config["NES"] = fake_exe_path
    temp_model.save_emulators_config()
    
    # 3. Create a BRAND NEW AppModel pointing to the same temp directory 
    # to simulate restarting the application
    new_model = AppModel(json_path=str(tmp_path / "test_inputs.json"))
    new_model.emulators_file = str(tmp_path / "emulators.json")
    
    # Manually trigger the load (since __init__ loads the default paths in our fixture)
    reloaded_config = new_model._load_emulators_config()
    
    # 4. Verify the custom path survived the "restart"
    assert reloaded_config["NES"] == fake_exe_path
    assert reloaded_config["SNES"] == "Default" # Others remain unaffected


# --- CATALOG FUSION TESTS ---

def test_get_installed_games_merges_steam_and_roms(temp_model, tmp_path):
    """Verifies that get_installed_games successfully combines Steam data and dynamic ROMs."""
    import json
    
    # 1. Fake a pre-existing Steam database
    steam_data = {
        "999": {
            "title": "Fake Steam Game",
            "exe_path": "steam://rungameid/999",
            "icon": ""
        }
    }
    with open(temp_model.steam_games_file, 'w', encoding='utf-8') as f:
        json.dump(steam_data, f)
        
    # 2. Add a fake ROM folder with one valid ROM
    rom_dir = tmp_path / "my_roms"
    rom_dir.mkdir()
    (rom_dir / "sonic.md").touch()
    temp_model.add_rom_folder(str(rom_dir))
    
    # 3. Call the master fusion method
    all_games = temp_model.get_installed_games()
    
    # 4. Assertions
    assert len(all_games) == 2
    
    # Check Steam game integration
    steam_game = next(g for g in all_games if g["title"] == "Fake Steam Game")
    assert steam_game["profile_file"] == "steam_games.json"
    
    # Check ROM integration
    rom_game = next(g for g in all_games if g["title"] == "sonic")
    assert rom_game["profile_file"] == "dinamico"


