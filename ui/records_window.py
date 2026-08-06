"""
Окно рекордов на PyQt5.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt

from core.config import BG, FG, ACCENT, BAR_BG, BTN_BG
from ui.styles import RECORDS_STYLE


class RecordsWindow(QDialog):
    def __init__(self, logic, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.setWindowTitle("🏆 Рекорды")
        self.setGeometry(100, 100, 500, 450)
        self.setStyleSheet(RECORDS_STYLE)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("🏆 Ваши рекорды")
        title.setObjectName("records_title")
        layout.addWidget(title)

        # Основной фрейм с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(6)

        records = self.logic.records
        point_price = self.logic.point_price

        record_items = [
            {"icon": "📌", "title": "Максимум точек за день", "value": records.get("max_points_per_day", 0), "color": "#00d4aa", "unit": "точек"},
            {"icon": "⚡", "title": "Максимум точек за спринт", "value": records.get("max_points_per_sprint", 0), "color": "#ffd166", "unit": "точек"},
            {"icon": "🚀", "title": "Максимальная скорость (за сессию)", "value": f"{records.get('max_speed_per_session', 0):.1f}", "color": "#ff6b6b", "unit": "точ/ч"},
            {"icon": "💨", "title": "Максимальная скорость (за день)", "value": f"{records.get('max_speed_per_day', 0):.1f}", "color": "#4ecdc4", "unit": "точ/ч"},
            {"icon": "💰", "title": "Максимум заработка за день", "value": f"{records.get('max_points_per_day', 0) * point_price:.2f}", "color": "#ffd700", "unit": "руб."},
            {"icon": "🏅", "title": "Всего точек за всё время", "value": self.logic.points, "color": "#a29bfe", "unit": "точек"},
            {"icon": "📅", "title": "Всего дней с активностью", "value": len(self.logic.get_daily_points_series()), "color": "#fd79a8", "unit": "дней"}
        ]

        for item in record_items:
            card = QFrame()
            card.setObjectName("record_card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 6, 10, 6)

            header = QHBoxLayout()
            title_label = QLabel(f"{item['icon']} {item['title']}")
            title_label.setObjectName("record_title")
            header.addWidget(title_label)
            header.addStretch()

            value_label = QLabel(f"{item['value']}")
            value_label.setObjectName("record_value")
            value_label.setStyleSheet(f"color: {item['color']};")
            header.addWidget(value_label)

            unit_label = QLabel(f" {item['unit']}")
            unit_label.setObjectName("record_unit")
            header.addWidget(unit_label)

            card_layout.addLayout(header)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)