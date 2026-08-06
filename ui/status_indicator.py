"""
Индикатор статуса (статичный светодиод).
"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class StatusIndicator(QLabel):
    """Статичный индикатор статуса."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setStyleSheet("border-radius: 8px; background-color: #2a2a40;")
    
    def set_active(self, active: bool):
        """Включить/выключить индикатор."""
        if active:
            self.setStyleSheet("border-radius: 8px; background-color: #00d4aa;")
        else:
            self.setStyleSheet("border-radius: 8px; background-color: #2a2a40;")