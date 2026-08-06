"""
Календарь активности (тепловая карта) на PyQt5.
"""
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
)
from PyQt5.QtCore import Qt

from core.config import BG, FG, ACCENT
from ui.styles import BASE_STYLE


class CalendarWidget(QWidget):
    def __init__(self, sessions, parent=None):
        super().__init__(parent)
        self.sessions = sessions
        self.setStyleSheet(BASE_STYLE)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title = QLabel("📅 Активность по дням")
        title.setStyleSheet(f"color: {ACCENT}; font-size: 14px; font-weight: 700;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Сетка для календаря
        grid = QGridLayout()
        grid.setSpacing(3)

        # Дни недели
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #888; font-size: 10px; font-weight: 600;")
            grid.addWidget(label, 0, i)

        # Генерируем данные за последние 6 недель
        today = datetime.now().date()
        start_date = today - timedelta(days=42)

        # Собираем точки по дням
        daily_data = {}
        for sess in self.sessions:
            try:
                day = datetime.fromtimestamp(sess.started_at).date()
                daily_data[day] = daily_data.get(day, 0) + sess.points
            except Exception:
                continue

        # Заполняем календарь
        current = start_date
        row = 1
        start_weekday = start_date.weekday()

        # Пустые ячейки в первой неделе
        for i in range(start_weekday):
            cell = QLabel("")
            cell.setFixedSize(30, 30)
            grid.addWidget(cell, row, i)

        while current <= today:
            col = current.weekday()
            points = daily_data.get(current, 0)

            cell = QLabel(str(current.day))
            cell.setAlignment(Qt.AlignCenter)
            cell.setFixedSize(30, 30)

            # Цвет в зависимости от количества точек
            if points == 0:
                color = "#2a2a40"
            elif points < 200:
                color = "#1a5a3a"
            elif points < 400:
                color = "#1a8a4a"
            elif points < 700:
                color = "#2a8a5a"
            elif points < 1000:
                color = "#3a8a6a"
            else:
                color = "#4a8a7a"

            cell.setStyleSheet(f"""
                background-color: {color};
                color: {FG};
                border-radius: 4px;
                font-size: 9px;
                font-weight: 500;
            """)

            cell.setToolTip(f"{current.strftime('%d.%m.%Y')}: {points} точек")

            grid.addWidget(cell, row, col)

            if col == 6:
                row += 1

            current += timedelta(days=1)

        # Пустые ячейки в последней неделе
        last_col = today.weekday()
        for i in range(last_col + 1, 7):
            cell = QLabel("")
            cell.setFixedSize(30, 30)
            grid.addWidget(cell, row, i)

        layout.addLayout(grid)

        # Легенда
        legend_layout = QHBoxLayout()
        legend_layout.setSpacing(10)
        legend_layout.addStretch()

        legend_data = [
            ("0", "#2a2a40"),
            ("1-199", "#1a5a3a"),
            ("200-399", "#1a8a4a"),
            ("400-699", "#2a8a5a"),
            ("700-999", "#3a8a6a"),
            ("1000+", "#4a8a7a")
        ]

        for text, color in legend_data:
            widget = QWidget()
            widget.setFixedSize(14, 14)
            widget.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            label = QLabel(text)
            label.setStyleSheet("color: #888; font-size: 9px;")
            legend_layout.addWidget(widget)
            legend_layout.addWidget(label)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # Информация о текущем дне
        today_points = daily_data.get(today, 0)
        info_label = QLabel(f"Сегодня: {today_points} точек")
        info_label.setStyleSheet(f"color: {ACCENT}; font-size: 11px; font-weight: 600;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)