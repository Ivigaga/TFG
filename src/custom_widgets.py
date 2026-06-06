from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen

class QRangeSlider(QWidget):
    # Emits (min_value, max_value)
    valuesChanged = Signal(int, int)

    # FIX 1: 'parent' must be the first argument for Qt Designer compatibility
    def __init__(self, parent=None):
        super().__init__(parent)
        self.min_val = 0
        self.max_val = 100
        self.low_thumb = 40
        self.high_thumb = 60
        self.current_val = 50  # Variable para mostrar el progreso azul
        self.setMinimumHeight(80)
        self.active_thumb = None

    def set_current_value(self, val):
        """Actualiza la barra azul de progreso en tiempo real"""
        self.current_val = max(self.min_val, min(self.max_val, val))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        
        # Dimensiones del riel (Mismas proporciones que tu scorebar)
        track_margin = 10
        track_x = track_margin
        track_y = h // 2 - 20
        track_w = w - 2 * track_margin
        track_h = 40
        radius = 8
        
        # 1. FONDO OSCURO DEL SLIDER (El riel visible)
        painter.setBrush(QColor("#222222"))
        pen = QPen(QColor("#555555"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(track_x, track_y, track_w, track_h, radius, radius)

        # 2. BARRA DE PROGRESO AZUL (Valor actual de la cámara)
        if self.current_val > self.min_val:
            blue_w = (self.current_val / self.max_val) * track_w
            
            # --- LÓGICA DE COLOR ---
            # Si el valor actual está fuera de la zona muerta (por debajo de low o por encima de high),
            # usamos el color FF5722 (naranja/rojo de activación).
            # Si está dentro, usamos el azul de reposo.
            is_outside = self.current_val < self.low_thumb or self.current_val > self.high_thumb
            
            color = QColor("#FF5722") if is_outside else QColor("#0078D7")
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            
            # Dibujamos respetando el borde gris
            painter.drawRoundedRect(track_x + 1, track_y + 1, int(blue_w) - 2, track_h - 2, radius - 1, radius - 1)

        # 3. ZONA MUERTA (Sombreado sutil opcional entre los pulgares)
        x_low = track_x + (self.low_thumb / self.max_val) * track_w
        x_high = track_x + (self.high_thumb / self.max_val) * track_w
        
        painter.setBrush(QColor(255, 255, 255, 15)) # 15 de opacidad para que no moleste
        painter.drawRect(int(x_low), track_y + 2, int(x_high - x_low), track_h - 4)

        # 4. LOS THUMBS (Líneas amarillas marcadoras)
        painter.setBrush(QColor("#FFEB3B"))
        painter.setPen(Qt.NoPen)
        thumb_w = 8
        
        # Dibujar thumb izquierdo
        painter.drawRect(int(x_low - thumb_w/2), track_y, thumb_w, track_h)
        # Dibujar thumb derecho
        painter.drawRect(int(x_high - thumb_w/2), track_y, thumb_w, track_h)

        # FIX 2: Close the painter to release resources and stop the console warning
        painter.end()

    def mousePressEvent(self, event):
        w = self.width()
        x = event.position().x()
        val = int(((x - 10) / (w - 20)) * self.max_val)
        
        if abs(val - self.low_thumb) < abs(val - self.high_thumb):
            self.active_thumb = "low"
        else:
            self.active_thumb = "high"

    def mouseMoveEvent(self, event):
        w = self.width()
        x = event.position().x()
        val = max(0, min(self.max_val, int(((x - 10) / (w - 20)) * self.max_val)))
        
        if self.active_thumb == "low" and val < self.high_thumb:
            self.low_thumb = val
        elif self.active_thumb == "high" and val > self.low_thumb:
            self.high_thumb = val
            
        self.update()
        self.valuesChanged.emit(self.low_thumb, self.high_thumb)

    def adjust_low_thumb(self, delta):
        """Ajusta de forma directa el marcador de límite inferior."""
        # Evitamos que baje de 0 o que supere al marcador superior
        self.low_thumb = max(self.min_val, min(self.high_thumb - 1, self.low_thumb + delta))
        self.update()
        self.valuesChanged.emit(self.low_thumb, self.high_thumb)

    def adjust_high_thumb(self, delta):
        """Ajusta de forma directa el marcador de límite superior."""
        # Evitamos que supere el máximo o que baje más allá del marcador inferior
        self.high_thumb = max(self.low_thumb + 1, min(self.max_val, self.high_thumb + delta))
        self.update()
        self.valuesChanged.emit(self.low_thumb, self.high_thumb)