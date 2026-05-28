import sys
from PySide6.QtWidgets import QApplication
from model import AppModel, get_asset_path
from view import MainView
from vision import VisionEngine
from presenter import MainPresenter


def main():
    app = QApplication(sys.argv)
    
    # 1. Cargar y aplicar la hoja de estilos externa
    ruta_estilos = get_asset_path("style.qss") # Cambia a .css si prefieres esa extensión
    try:
        with open(ruta_estilos, "r", encoding="utf-8") as archivo_estilo:
            app.setStyleSheet(archivo_estilo.read())
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo de estilos en {ruta_estilos}.")

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
        sys.exit(0)  # Forzar salida completa de la aplicación
    view.closeEvent = custom_close

    # Start the app
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()