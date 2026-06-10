import sys
from PySide6.QtWidgets import QApplication, QMessageBox  # <-- Añadir QMessageBox aquí
from model import AppModel, get_asset_path
from view import MainView
from vision import VisionEngine
from presenter import MainPresenter

def main():
    app = QApplication(sys.argv)
    
    # 1. Cargar y aplicar la hoja de estilos externa
    ruta_estilos = get_asset_path("style.qss") 
    try:
        with open(ruta_estilos, "r", encoding="utf-8") as archivo_estilo:
            app.setStyleSheet(archivo_estilo.read())
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo de estilos en {ruta_estilos}.")

    # 1. Instantiate the Model (Data & Logic)
    model = AppModel("controls/default_inputs.json")
    
    # 2. Instantiate the Vision Engine (Hardware/AI) con manejo de errores
    try:
        vision_engine = VisionEngine(model.model_path, model.target_fps)
    except Exception as e:
        # Si la cámara falla, mostramos un mensaje gráfico y cerramos
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error Crítico")
        msg_box.setText("No se ha detectado ninguna cámara web.")
        msg_box.setInformativeText("Por favor, conecta una cámara al equipo y vuelve a iniciar la aplicación.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        sys.exit(1)  # Cierre controlado devolviendo código de error
    
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
    
    # Start the GUI loop
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()