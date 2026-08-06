"""
Плавающий мини-виджет на PyQt5.
Отображает скорость и время до конца спринта.
Всегда поверх всех окон.
"""
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QApplication, QMenu, QSystemTrayIcon, QAction
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette

from ui.styles import FLOATING_STYLE
from core.utils import calc_points_per_hour, get_productive_tab_time
from core.config import BG, FG, ACCENT, BAR_BG


class FloatingWidget(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.setStyleSheet(FLOATING_STYLE)
        self.drag_pos = QPoint()

        # Настройки окна
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # Без рамки
            Qt.WindowStaysOnTopHint |     # Всегда поверх
            Qt.Tool |                     # Не отображается в панели задач
            Qt.WindowDoesNotAcceptFocus   # Не перехватывает фокус
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 80)
        
        # Позиция по умолчанию (правый верхний угол)
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 220, 20)

        # Основной фрейм
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("main_frame")
        self.main_frame.setGeometry(0, 0, 200, 80)

        # Вертикальный макет
        layout = QVBoxLayout(self.main_frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)

        # Скорость
        self.speed_label = QLabel("Скорость: —")
        self.speed_label.setObjectName("speed_label")
        self.speed_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.speed_label)

        # Время
        self.time_label = QLabel("До конца: —")
        self.time_label.setObjectName("time_label")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        # Таймер обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_content)
        self.timer.start(1000)  # 1 секунда

        self._update_content()

    # ---------- Перетаскивание ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """Двойной клик - закрыть виджет."""
        if event.button() == Qt.LeftButton:
            self.close()
            event.accept()

    # ---------- Контекстное меню ----------
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        close_action = QAction("Закрыть", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec_(event.globalPos())

    # ---------- Обновление содержимого ----------
    def _update_content(self):
        try:
            # Скорость
            speed_text = "Скорость: —"
            if self.logic.session_active and self.logic.session_points > 0:
                prod_time = self.logic.get_current_productive_seconds()
                speed = calc_points_per_hour(self.logic.session_points, prod_time)
                if speed is not None:
                    speed_text = f"⚡ {speed:.0f} т/ч"
            else:
                total_points = self.logic.points
                total_prod = 0.0
                for s in self.logic.sessions:
                    total_prod += get_productive_tab_time(s.tab_times)
                speed = calc_points_per_hour(total_points, total_prod)
                if speed is not None:
                    speed_text = f"⚡ {speed:.0f} т/ч (ср.)"
            self.speed_label.setText(speed_text)

            # Оставшееся время
            time_text = "До конца: —"
            if self.logic.session_active:
                phase, remaining, _ = self.logic._update_phase_progress()
                if phase == "sprint":
                    mins, secs = divmod(int(remaining), 60)
                    time_text = f"⏱ {mins:02d}:{secs:02d}"
                elif phase == "break":
                    mins, secs = divmod(int(remaining), 60)
                    time_text = f"☕ {mins:02d}:{secs:02d}"
                elif self.logic.sprint_finished:
                    time_text = "✅ Готово"
                else:
                    time_text = "⏸ Сессия активна"
            self.time_label.setText(time_text)
        except Exception:
            pass

    # ---------- Показывать/скрывать ----------
    def show(self):
        super().show()
        self.raise_()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()