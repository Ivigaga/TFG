"""
Punto de Entrada Principal (Main) de la Aplicación

Este archivo es el responsable de inicializar la aplicación y ensamblar
los tres componentes principales de la arquitectura MVP (Modelo-Vista-Presentador),
junto con el motor de visión por computador en un hilo separado.
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from model import AppModel, get_asset_path
from view import MainView
from vision import VisionEngine
from presenter import MainPresenter

def main():
    # Inicializamos el motor principal de la interfaz gráfica de Qt
    app = QApplication(sys.argv)
    
    # ==========================================
    # 0. CARGAR ESTILOS (UI)
    # ==========================================
    # Cargamos y aplicamos la hoja de estilos externa para toda la aplicación
    ruta_estilos = get_asset_path("style.qss") 
    try:
        with open(ruta_estilos, "r", encoding="utf-8") as archivo_estilo:
            app.setStyleSheet(archivo_estilo.read())
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el archivo de estilos en {ruta_estilos}.")

    # ==========================================
    # 1. INICIALIZAR EL MODELO (Datos y Lógica)
    # ==========================================
    # Creamos el modelo cargando la configuración base de controles
    model = AppModel("controls/default_inputs.json")
    
    # ==========================================
    # 2. INICIALIZAR MOTOR DE VISIÓN (Hardware e IA)
    # ==========================================
    # Intentamos arrancar la cámara y cargar el modelo de MediaPipe
    try:
        vision_engine = VisionEngine(model.model_path, model.target_fps)
    except Exception as e:
        # Manejo de fallos: Si el equipo no tiene cámara web física o está bloqueada,
        # mostramos un mensaje gráfico amigable al usuario en lugar de colapsar la consola.
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error Crítico")
        msg_box.setText("No se ha detectado ninguna cámara web.")
        msg_box.setInformativeText("Por favor, conecta una cámara al equipo y vuelve a iniciar la aplicación.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
        sys.exit(1)  # Cierre controlado de la aplicación devolviendo código de error
    
    # ==========================================
    # 3. INICIALIZAR LA VISTA (Interfaz Gráfica)
    # ==========================================
    # Creamos la ventana principal (solo se dibuja, aún no tiene lógica)
    view = MainView()
    
    # ==========================================
    # 4. INICIALIZAR EL PRESENTADOR (El Cerebro)
    # ==========================================
    # Inyectamos el Modelo, la Vista y el Motor de Visión en el Presentador.
    # Aquí es donde se conectan todas las señales y la aplicación "cobra vida".
    presenter = MainPresenter(view, model, vision_engine)
    
    # ==========================================
    # 5. GESTIÓN DEL CIERRE DE LA APLICACIÓN
    # ==========================================
    # Interceptamos el evento de cierre de la ventana (cuando se pulsa la 'X')
    original_close_event = view.closeEvent
    
    def custom_close(event):
        # Aseguramos que el Presentador libere los recursos limpiamente:
        # (Detener la cámara, matar el hilo del QThread y desconectar el mando virtual)
        presenter.shutdown()
        original_close_event(event)
        
    # Reemplazamos el comportamiento por defecto con nuestra función segura
    view.closeEvent = custom_close
    
    # ==========================================
    # 6. ARRANQUE DEL BUCLE PRINCIPAL
    # ==========================================
    # Mostramos la ventana y cedemos el control al bucle de eventos de PySide6
    view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()