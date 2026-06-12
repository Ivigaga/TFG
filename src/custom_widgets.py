"""
MÓDULO custom_widgets.py
---------------------------------------------------------
Contiene componentes visuales (Widgets) personalizados creados desde cero
mediante la API de dibujo de Qt (QPainter).
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen

class QRangeSlider(QWidget):
    """
    Control deslizante (Slider) personalizado con DOS selectores (thumbs).
    Permite definir un rango de zona muerta (valor mínimo y máximo) 
    y muestra visualmente una barra de progreso que indica el estado del sensor actual.
    """
    
    # Señal emitida cuando el usuario mueve alguno de los dos marcadores: (valor_minimo, valor_maximo)
    valuesChanged = Signal(int, int)

    # FIX 1: 'parent' debe ser el primer argumento para garantizar la compatibilidad con Qt Designer
    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_val = 0      # Valor mínimo absoluto
        self.max_val = 100    # Valor máximo absoluto
        self.low_thumb = 40   # Posición inicial del marcador inferior
        self.high_thumb = 60  # Posición inicial del marcador superior
        
        self.current_val = 50 # Variable para mostrar la barra azul de progreso de la cara
        self.setMinimumHeight(80)
        self.active_thumb = None # Registra qué marcador está arrastrando el ratón en este momento

    def set_current_value(self, val):
        """Actualiza la barra azul de progreso en tiempo real basada en el movimiento del usuario."""
        self.current_val = max(self.min_val, min(self.max_val, val))
        self.update() # Fuerza a Qt a redibujar el widget (llama a paintEvent)

    def paintEvent(self, event):
        """
        Método central de renderizado de Qt. Dibuja geométricamente todas las partes del Slider.
        Se ejecuta cada vez que el widget necesita actualizarse visualmente.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Suavizado para evitar bordes dentados

        w, h = self.width(), self.height()
        
        # Dimensiones del riel base (calculadas dinámicamente según el tamaño del widget)
        track_margin = 10
        track_x = track_margin
        track_y = h // 2 - 20
        track_w = w - 2 * track_margin
        track_h = 40
        radius = 8
        
        # 1. FONDO OSCURO DEL SLIDER (El riel vacío)
        painter.setBrush(QColor("#222222"))
        pen = QPen(QColor("#555555"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(track_x, track_y, track_w, track_h, radius, radius)

        # 2. BARRA DE PROGRESO DE LA CARA (Valor actual posicional)
        if self.current_val > self.min_val:
            blue_w = (self.current_val / self.max_val) * track_w
            
            # --- LÓGICA DE COLOR DE ACTIVACIÓN ---
            # Si el valor actual está fuera de la zona muerta (por debajo del thumb inferior o 
            # por encima del superior), cambiamos el color a naranja/rojo para indicar "Acción disparada".
            # Si está dentro, usamos el azul de "Reposo".
            is_outside = self.current_val < self.low_thumb or self.current_val > self.high_thumb
            
            color = QColor("#FF5722") if is_outside else QColor("#0078D7")
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            
            # Dibujamos la barra coloreada respetando el grosor del borde gris
            painter.drawRoundedRect(track_x + 1, track_y + 1, int(blue_w) - 2, track_h - 2, radius - 1, radius - 1)

        # 3. ZONA MUERTA (Sombreado semitransparente entre los dos selectores)
        x_low = track_x + (self.low_thumb / self.max_val) * track_w
        x_high = track_x + (self.high_thumb / self.max_val) * track_w
        
        # Usamos canal Alfa (15 de opacidad) para que sea sutil
        painter.setBrush(QColor(255, 255, 255, 15)) 
        painter.drawRect(int(x_low), track_y + 2, int(x_high - x_low), track_h - 4)

        # 4. LOS SELECTORES (Thumbs / Líneas amarillas marcadoras)
        painter.setBrush(QColor("#FFEB3B"))
        painter.setPen(Qt.NoPen)
        thumb_w = 8
        
        # Dibujar marcador izquierdo
        painter.drawRect(int(x_low - thumb_w/2), track_y, thumb_w, track_h)
        # Dibujar marcador derecho
        painter.drawRect(int(x_high - thumb_w/2), track_y, thumb_w, track_h)

        # FIX 2: Cerrar el QPainter para liberar memoria de GPU y evitar advertencias en consola
        painter.end()

    def mousePressEvent(self, event):
        """Detecta sobre cuál de los dos selectores ha hecho clic el usuario basándose en proximidad."""
        w = self.width()
        x = event.position().x()
        
        # Convierte la posición física en píxeles a un valor matemático de 0 a 100
        val = int(((x - 10) / (w - 20)) * self.max_val)
        
        # Asigna el control al marcador que esté más cerca del clic del ratón
        if abs(val - self.low_thumb) < abs(val - self.high_thumb):
            self.active_thumb = "low"
        else:
            self.active_thumb = "high"

    def mouseMoveEvent(self, event):
        """Permite arrastrar el selector activo actualizando su valor lógico."""
        w = self.width()
        x = event.position().x()
        # Calculamos la nueva posición asegurándonos de no salirnos de los límites [0, 100]
        val = max(0, min(self.max_val, int(((x - 10) / (w - 20)) * self.max_val)))
        
        # Impedimos que el marcador inferior supere al superior (y viceversa)
        if self.active_thumb == "low" and val < self.high_thumb:
            self.low_thumb = val
        elif self.active_thumb == "high" and val > self.low_thumb:
            self.high_thumb = val
            
        self.update() # Forzar repintado visual
        self.valuesChanged.emit(self.low_thumb, self.high_thumb) # Notificar al presentador del cambio

    def adjust_low_thumb(self, delta):
        """Ajusta programáticamente (mediante botones +/-) el marcador de límite inferior."""
        # Evitamos que baje de 0 o que "choque" con el marcador superior
        self.low_thumb = max(self.min_val, min(self.high_thumb - 1, self.low_thumb + delta))
        self.update()
        self.valuesChanged.emit(self.low_thumb, self.high_thumb)

    def adjust_high_thumb(self, delta):
        """Ajusta programáticamente (mediante botones +/-) el marcador de límite superior."""
        # Evitamos que supere el 100 o que baje más allá del marcador inferior
        self.high_thumb = max(self.low_thumb + 1, min(self.max_val, self.high_thumb + delta))
        self.update()
        self.valuesChanged.emit(self.low_thumb, self.high_thumb)