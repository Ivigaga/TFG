import pytest
from unittest.mock import MagicMock, patch
from presenter import MainPresenter

@pytest.fixture
def setup_presenter():
    """Injects fake View, Model, and Vision components into the Presenter."""
    mock_view = MagicMock()
    mock_model = MagicMock()
    mock_vision = MagicMock()
    
    presenter = MainPresenter(mock_view, mock_model, mock_vision)
    
    # We mock the physical gamepad to avoid actual driver calls during tests
    presenter.gamepad = MagicMock() 
    
    return presenter, mock_view, mock_model

def test_execute_press_action_gamepad(setup_presenter):
    """Verifies that a gamepad action correctly calls the virtual gamepad driver."""
    presenter, _, _ = setup_presenter
    
    # Simulate a payload coming from the main loop
    input_data = {"input": "XUSB_GAMEPAD_A"}
    
    presenter._execute_press_action(input_data)
    
    # Assert that the gamepad's press_button method was called exactly once
    expected_button_id = presenter.buttons_map["XUSB_GAMEPAD_A"]
    presenter.gamepad.press_button.assert_called_once_with(button=expected_button_id)

def test_execute_press_action_system_restore(setup_presenter):
    """Verifies that the SYS_RESTORE_APP action commands the view to unminimize."""
    presenter, mock_view, _ = setup_presenter
    
    # Simulate the user triggering the restore gesture
    input_data = {"input": "SYS_RESTORE_APP", "active": False}
    
    presenter._execute_press_action(input_data)
    
    # Assert that the presenter commanded the view to show itself
    mock_view.showNormal.assert_called_once()
    mock_view.activateWindow.assert_called_once()

@patch("PySide6.QtWidgets.QApplication.focusWidget")
def test_navigation_blocked_when_minimized(mock_focus_widget, setup_presenter):
    """Verifies that facial navigation is completely ignored if the app is hidden."""
    presenter, mock_view, _ = setup_presenter
    
    # --- SCENARIO 1: Window is Minimized ---
    # Tell the fake view to pretend it is minimized
    mock_view.isMinimized.return_value = True
    
    # Attempt to navigate
    presenter.navigate_interface("DOWN")
    
    # VERIFICATION 1: The lock worked. It aborted before reaching Qt logic.
    mock_focus_widget.assert_not_called()
    
    # --- SCENARIO 2: Window is Restored ---
    # Now pretend the window is fully visible
    mock_view.isMinimized.return_value = False
    
    # Attempt to navigate again
    presenter.navigate_interface("DOWN")
    
    # VERIFICATION 2: The lock opened. It reached the Qt internal logic.
    mock_focus_widget.assert_called_once()


def test_start_video(setup_presenter):
    """Verifies that starting the video feed correctly initializes the Vision component."""
    presenter, _, _ = setup_presenter
    
    # Usamos presenter.vision directamente para no equivocarnos de Mock
    presenter.vision.isRunning.return_value = False
    
    presenter.start_video()
    
    # Assert that the Vision component's start method was called
    presenter.vision.start.assert_called_once()

def test_start_video_already_started(setup_presenter):
    """Verifies that starting the video feed when it's already running does not cause errors."""
    presenter, _, _ = setup_presenter
    
    # Simulate the video feed already being active
    presenter.vision.isRunning.return_value = True
    
    presenter.start_video()
    
    # Assert that the Vision component's start method was not called again
    presenter.vision.start.assert_not_called()


# --- FRAME PROCESSING TESTS ---

@patch("presenter.cv2.cvtColor")
@patch("presenter.QImage")
@patch("presenter.QPixmap")
def test_on_frame_processed_video_paused(mock_pixmap, mock_image, mock_cvtcolor, setup_presenter):
    """Verifies that if the video is paused, the frame is completely ignored."""
    presenter, mock_view, mock_model = setup_presenter
    mock_view.pip_window=MagicMock()  # Ensure pip_window exists to avoid attribute errors
    mock_view.pip_window.isVisible.return_value = True  # Assume PiP is visible to isolate the test to just the video playing state
    # 1. Pause the video
    presenter.is_video_playing = False
    
    # 2. Send a dummy frame
    presenter._on_frame_processed(frame=MagicMock(), blendshapes={}, landmarks=[], is_new_processing=True)
    
    # 3. Verify the early return worked: nothing else should have happened
    mock_model.update_gesture_scores.assert_not_called()
    mock_cvtcolor.assert_not_called()
    mock_view.update_main_video.assert_not_called()


@patch("presenter.MainPresenter._process_gamepad_logic")
@patch("presenter.cv2.cvtColor")
@patch("presenter.QImage")
@patch("presenter.QPixmap")
def test_on_frame_processed_new_data(mock_pixmap, mock_image, mock_cvtcolor, mock_gamepad_logic, setup_presenter):
    """Verifies that new processing data updates the model and triggers gamepad logic."""
    presenter, mock_view, mock_model = setup_presenter
    presenter.is_video_playing = True
    mock_view.pip_window=False  # Ensure pip_window exists to avoid attribute errors
    # Create a fake image frame to satisfy OpenCV/Qt shape requirements
    dummy_frame = MagicMock()
    dummy_frame.shape = (480, 640, 3) 
    mock_cvtcolor.return_value = dummy_frame
    
    dummy_blendshapes = {"smile": 0.8}
    dummy_landmarks = ["fake_nose_coords"]
    
    # 1. Process WITH new AI data
    presenter._on_frame_processed(dummy_frame, dummy_blendshapes, dummy_landmarks, is_new_processing=True)
    
    # 2. Verify the core logic was executed
    mock_model.update_gesture_scores.assert_called_once_with(dummy_blendshapes)
    mock_gamepad_logic.assert_called_once_with(dummy_landmarks)
    
    # 3. Verify the video frame was sent to the view
    mock_view.update_main_video.assert_called_once()


@patch("presenter.MainPresenter._process_gamepad_logic")
@patch("presenter.cv2.cvtColor")
@patch("presenter.QImage")
@patch("presenter.QPixmap")
def test_on_frame_processed_no_new_data(mock_pixmap, mock_image, mock_cvtcolor, mock_gamepad_logic, setup_presenter):
    """Verifies that if there's no new AI data, it skips logic but still renders the video."""
    presenter, mock_view, mock_model = setup_presenter
    presenter.is_video_playing = True
    mock_view.pip_window=False  # Ensure pip_window exists to avoid attribute errors

    dummy_frame = MagicMock()
    dummy_frame.shape = (480, 640, 3)
    mock_cvtcolor.return_value = dummy_frame
    
    # 1. Process WITHOUT new data (e.g., between AI frames to maintain 60 FPS video)
    presenter._on_frame_processed(dummy_frame, {}, [], is_new_processing=False)
    
    # 2. Verify the heavy AI/Gamepad logic was SKIPPED
    mock_model.update_gesture_scores.assert_not_called()
    mock_gamepad_logic.assert_not_called()
    
    # 3. Verify the video frame was STILL rendered to maintain visual fluidity
    mock_view.update_main_video.assert_called_once()


@patch("presenter.time.perf_counter")
@patch("presenter.cv2.cvtColor")
@patch("presenter.QImage")
@patch("presenter.QPixmap")
def test_on_frame_processed_ui_score_update(mock_pixmap, mock_image, mock_cvtcolor, mock_time, setup_presenter):
    """Verifies that the UI progress bar is updated when calibrating a gesture."""
    presenter, mock_view, mock_model = setup_presenter
    presenter.is_video_playing = True
    mock_view.pip_window=MagicMock()  # Ensure pip_window exists to avoid attribute errors
    mock_view.pip_window.isVisible.return_value = True  # Assume PiP is visible to isolate the test to just the video playing state
    # 1. Simulate we are in the calibration screen
    presenter.is_reading_score = True
    presenter.current_mapped_gesture = "smile"
    
    # Fake the model returning a score of 0.85 (85%) and the view slider at 50%
    mock_model.get_score.return_value = 0.85
    mock_view.get_slider_threshold.return_value = 50
    
    # Fast forward time to bypass the 0.1s UI cooldown lock
    presenter.last_ui_update_time = 0
    mock_time.return_value = 1.0 
    
    dummy_frame = MagicMock()
    dummy_frame.shape = (480, 640, 3)
    mock_cvtcolor.return_value = dummy_frame
    
    # 2. Run the frame
    presenter._on_frame_processed(dummy_frame, {}, [], is_new_processing=False)
    
    # 3. Verify the view was commanded to update the score bar: 85 score, True (surpassed threshold)
    mock_view.update_score_bar.assert_called_once_with(85, True)


# --- GAMEPAD LOGIC TESTS ---

@patch("presenter.MainPresenter._execute_release_action")
@patch("presenter.MainPresenter._execute_press_action")
def test_process_gamepad_logic_triggers_press(mock_press, mock_release, setup_presenter):
    """Verifies that exceeding the threshold triggers a press action."""
    presenter, _, mock_model = setup_presenter
    
    # 1. Configurar el estado simulado del modelo
    # El usuario sonríe (score 0.8) superando el umbral (0.5). Aún no estaba activo.
    mock_model.input_structure = {
        "smile": {
            "category_type": "gamepad",
            "input": "XUSB_GAMEPAD_A",
            "threshold": 0.5,
            "score": 0.8,
            "active": False 
        }
    }
    
    # 2. Ejecutar la lógica (pasando una lista vacía de landmarks como simulacro)
    presenter._process_gamepad_logic([])
    
    # 3. Verificaciones
    mock_press.assert_called_once()
    mock_release.assert_not_called()
    
    # El presentador debe haber marcado el gesto como activo para no volver a pulsarlo en el siguiente frame
    assert mock_model.input_structure["smile"]["active"] is True


@patch("presenter.MainPresenter._execute_release_action")
@patch("presenter.MainPresenter._execute_press_action")
def test_process_gamepad_logic_triggers_release(mock_press, mock_release, setup_presenter):
    """Verifies that dropping below the threshold triggers a release action."""
    presenter, _, mock_model = setup_presenter
    
    # 1. Configurar el estado simulado del modelo
    # El usuario dejó de sonreír (score 0.2). El botón estaba físicamente apretado (active: True).
    mock_model.input_structure = {
        "smile": {
            "category_type": "gamepad",
            "input": "XUSB_GAMEPAD_A",
            "threshold": 0.5,
            "score": 0.2,
            "active": True 
        }
    }
    
    # 2. Ejecutar la lógica
    presenter._process_gamepad_logic([])
    
    # 3. Verificaciones
    mock_release.assert_called_once()
    mock_press.assert_not_called()
    
    # El presentador debe haber liberado el gesto
    assert mock_model.input_structure["smile"]["active"] is False



@patch("presenter.MainPresenter.navigate_interface")
def test_process_gamepad_logic_nose_centered(mock_navigate, setup_presenter):
    """Verifies that if the nose is in the deadzone, no movement is triggered."""
    # 1. Recuperamos el mock_model del fixture
    presenter, _, mock_model = setup_presenter
    
    # --- FIX: Le damos un diccionario real para que los .get() devuelvan números ---
    mock_model.input_structure = {}
    mock_model.is_continuous_mode = True
    
    # 2. Creamos un punto facial simulado en el centro exacto (0.5, 0.5)
    nose_landmark = MagicMock()
    nose_landmark.x = 0.5
    nose_landmark.y = 0.5
    fake_landmarks = [MagicMock(), nose_landmark] 
    
    presenter._process_gamepad_logic(fake_landmarks)
    
    # 3. Verificaciones
    presenter.gamepad.left_joystick.assert_called_with(x_value=0, y_value=0)
    mock_navigate.assert_not_called()
    presenter.gamepad.update.assert_called_once()


@patch("presenter.MainPresenter.navigate_interface")
def test_process_gamepad_logic_nose_movement(mock_navigate, setup_presenter):
    """Verifies that moving the nose triggers the correct joystick values and navigation."""
    # 1. Recuperamos el mock_model del fixture
    presenter, _, mock_model = setup_presenter
    
    # --- FIX: Le damos un diccionario real ---
    mock_model.input_structure = {}
    mock_model.is_continuous_mode = True
    
    # 2. Simulamos que el usuario mueve la cabeza hacia la DERECHA y ARRIBA
    nose_landmark = MagicMock()
    nose_landmark.x = 0.2
    nose_landmark.y = 0.2
    fake_landmarks = [MagicMock(), nose_landmark] 
    
    presenter._process_gamepad_logic(fake_landmarks)
    
    # 3. Verificamos que se calculó la geometría correcta
    presenter.gamepad.left_joystick.assert_called_with(x_value=20000, y_value=20000)
    mock_navigate.assert_any_call("RIGHT")
    mock_navigate.assert_any_call("UP")


@patch("presenter.MainPresenter.navigate_interface")
def test_process_gamepad_logic_step_mode(mock_navigate, setup_presenter):
    """Verifies that continuous mode restriction zeroes out the joystick to prevent spam."""
    presenter, _, mock_model = setup_presenter
    
    # 1. Apagamos el modo continuo
    mock_model.is_continuous_mode = False
    
    # Simulamos que en el frame anterior el usuario YA estaba moviéndose a la izquierda
    mock_model.input_structure = {
        "noseLeft": {"active": True, "threshold": 0.6},
        "noseRight": {"active": False},
        "noseUp": {"active": False},
        "noseDown": {"active": False}
    }
    
    # El usuario SIGUE con la cabeza a la izquierda (x > 0.6)
    nose_landmark = MagicMock()
    nose_landmark.x = 0.8
    nose_landmark.y = 0.5
    fake_landmarks = [MagicMock(), nose_landmark] 
    
    presenter._process_gamepad_logic(fake_landmarks)
    
    # 2. Verificaciones
    # Gracias a tu código 'jx = 0', el joystick no debe recibir -20000 este frame
    presenter.gamepad.left_joystick.assert_called_with(x_value=0, y_value=0)
    
    # La interfaz gráfica no debe navegar de nuevo, bloqueando el movimiento


# --- GAME LAUNCHER TESTS ---

@patch("presenter.os.startfile")
def test_handle_game_launch_steam_or_native(mock_startfile, setup_presenter):
    """Verifies that Steam URIs and native .exe files are launched natively and the app minimizes."""
    presenter, mock_view, _ = setup_presenter
    
    # Simulate launching a Steam game
    steam_uri = "steam://rungameid/123450"
    presenter.handle_game_launch(steam_uri)
    
    # Verify OS was commanded to open the URI
    mock_startfile.assert_called_once_with(steam_uri)
    
    # Verify the UI minimized itself to let the user play
    mock_view.showMinimized.assert_called_once()


@patch("presenter.subprocess.Popen")
@patch("presenter.os.path.exists", return_value=True)
def test_handle_game_launch_custom_emulator(mock_exists, mock_popen, setup_presenter):
    """Verifies that ROMs trigger the assigned custom emulator via subprocess."""
    presenter, mock_view, mock_model = setup_presenter
    
    # 1. Setup the fake model knowledge
    mock_model.get_console_from_extension.return_value = "NES"
    mock_model.emulators_config = {"NES": "C:\\Emulators\\fceux.exe"}
    
    rom_path = "C:\\Games\\mario.nes"
    
    # 2. Launch!
    presenter.handle_game_launch(rom_path)
    
    # 3. Verify it used Popen with the correct arguments [emulator, rom]
    mock_popen.assert_called_once_with(["C:\\Emulators\\fceux.exe", rom_path])
    mock_view.showMinimized.assert_called_once()


# --- EXPLORER ROUTING TESTS ---

@patch("presenter.MainPresenter.refresh_explorer")
@patch("presenter.os.path.dirname")
def test_explorer_up_hits_drives_root(mock_dirname, mock_refresh, setup_presenter):
    """Verifies that navigating 'UP' from C:\ switches the view to the Hard Drives list."""
    presenter, _, _ = setup_presenter
    
    # 1. Simulate we are at the root of a drive
    presenter.current_explorer_path = "C:\\"
    
    # The OS returns C:\ as the parent of C:\. This is how we know we hit the ceiling.
    mock_dirname.return_value = "C:\\" 
    
    # 2. Go Up
    presenter.handle_explorer_up()
    
    # 3. Verify it switched to DRIVES mode
    assert presenter.current_explorer_path == "DRIVES"
    mock_refresh.assert_called_once()


def test_handle_emulator_exe_chosen(setup_presenter):
    """Verifies that clicking an emulator updates the config and repopulates the view."""
    presenter, mock_view, mock_model = setup_presenter
    
    # 1. Simulate the user was setting up the SNES emulator inside C:\Emulators
    presenter.current_setup_console = "SNES"
    presenter.current_explorer_path = "C:\\Emulators"
    mock_model.emulators_config = {}
    
    # 2. The user clicks the exe
    presenter.handle_emulator_exe_chosen("snes9x.exe")
    
    # 3. Verifications
    expected_path = "C:\\Emulators\\snes9x.exe"
    assert mock_model.emulators_config["SNES"] == expected_path
    
    mock_model.save_emulators_config.assert_called_once()
    mock_view.populate_emulator_settings.assert_called_once()
    mock_view.show_page.assert_called_with(8)


# --- VIDEO TOGGLE TESTS ---

def test_toggle_video_states(setup_presenter):
    """Verifies that the play/pause button correctly switches states and UI text."""
    # --- FIX: El tercer elemento es el modelo, lo ignoramos con '_' ---
    presenter, mock_view, _ = setup_presenter
    
    # Initial state (Playing)
    presenter.is_video_playing = True
    
    # 1. Toggle to PAUSE
    presenter.toggle_video()
    assert presenter.is_video_playing is False
    mock_view.ui.stopButton.setText.assert_called_with("Resume Video")
    
    # 2. Toggle back to PLAY
    presenter.vision.isRunning.return_value = False
    presenter.toggle_video()
    
    assert presenter.is_video_playing is True
    mock_view.ui.stopButton.setText.assert_called_with("Pause Video")
    
    # --- FIX: Le preguntamos a la visión del presentador, no a una variable suelta ---
    presenter.vision.start.assert_called_once()