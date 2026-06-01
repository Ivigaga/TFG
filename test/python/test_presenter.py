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