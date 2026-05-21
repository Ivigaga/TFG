import sys
from PySide6.QtWidgets import QApplication
from model import AppModel
from view import MainView
from vision import VisionEngine
from presenter import MainPresenter

def main():
    app = QApplication(sys.argv)
    
    # 1. Instantiate the Model (Data & Logic)
    model = AppModel("default_inputs.json")
    
    # 2. Instantiate the Vision Engine (Hardware/AI)
    vision_engine = VisionEngine(model.model_path, model.target_fps)
    
    # 3. Instantiate the View (GUI)
    view = MainView()
    
    # 4. Instantiate the Presenter (The Brain connecting everything)
    presenter = MainPresenter(view, model, vision_engine)
    
    # Override the View's close event to cleanly shutdown the Presenter
    original_close_event = view.closeEvent
    def custom_close(event):
        presenter.shutdown()
        original_close_event(event)
    view.closeEvent = custom_close

    # Start the app
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()