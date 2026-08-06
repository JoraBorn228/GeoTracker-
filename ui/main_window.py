"""
Главное окно приложения на PyQt5.
"""
import sys
import time
import random
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame, QMessageBox, QInputDialog,
    QDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from core.config import (
    WINDOW_W, WINDOW_H, BG, FG, ACCENT, LEVEL_COLOR, BG_FLASH,
    BAR_BG, BAR_FG, GOAL_BAR_FG, BTN_BG, BTN_ACTIVE, BTN_STOP,
)
from core.models import Particle
from core.utils import (
    format_duration, format_points_per_hour,
    is_productive_tab, get_productive_tab_time,
    calc_points_per_hour, calc_level,
)
from core.logic import TrackerLogic
from storage.storage import save_progress
from storage.settings_manager import load_settings, save_settings
from ui.styles import MAIN_STYLE, ADVICE_STYLE, BASE_STYLE
from ui.status_indicator import StatusIndicator


class MainWindow(QMainWindow):
    def __init__(self, logic: TrackerLogic):
        super().__init__()
        self.logic = logic
        self.logic.on_update = self._refresh_all
        self.logic.on_beep = self._beep
        self.logic.on_level_up = self._level_up_effect

        # Переменные для анимации
        self.particles: list[Particle] = []
        self.points_scale = 1.0
        self._last_today_points = 0

        # Окна
        self.stats_window: Optional['QMainWindow'] = None
        self.settings_window: Optional['QMainWindow'] = None
        self.charts_window: Optional['QMainWindow'] = None
        self.records_window: Optional['QMainWindow'] = None
        self.floating_widget: Optional['QMainWindow'] = None

        self._setup_ui()
        self.logic.register_hotkey()
        self._check_goal_adjustment()

        # Таймер анимации
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(16)

        # Таймер автосохранения
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self._auto_save)
        self.save_timer.start(self.logic.auto_save_interval * 1000)

    # ---------- Интерфейс ----------
    def _setup_ui(self):
        self.setWindowTitle("Картограф")
        self.setFixedSize(WINDOW_W, WINDOW_H)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        self.setStyleSheet(MAIN_STYLE)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(14, 10, 14, 14)
        layout.setSpacing(4)

        # --- Верхняя панель ---
        top_frame = QFrame()
        top_frame.setObjectName("top_frame")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(4, 4, 4, 4)

        self.rank_label = QLabel("Стажёр")
        self.rank_label.setObjectName("rank_label")
        top_layout.addWidget(self.rank_label)
        top_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)

        self.settings_btn = self._create_btn("⚙️", self._show_settings)
        btn_layout.addWidget(self.settings_btn)

        self.stats_btn = self._create_btn("📊", self._show_stats)
        btn_layout.addWidget(self.stats_btn)

        self.charts_btn = self._create_btn("📈", self._show_charts)
        btn_layout.addWidget(self.charts_btn)

        self.records_btn = self._create_btn("🏆", self._show_records)
        btn_layout.addWidget(self.records_btn)

        self.floating_btn = self._create_btn("🖥", self._toggle_floating)
        btn_layout.addWidget(self.floating_btn)

        self.advice_btn = self._create_btn("💡", self._show_advice)
        btn_layout.addWidget(self.advice_btn)

        self.calendar_btn = self._create_btn("📅", self._show_calendar)
        btn_layout.addWidget(self.calendar_btn)

        top_layout.addLayout(btn_layout)
        layout.addWidget(top_frame)

        # --- Счётчик ---
        self.points_label = QLabel("0")
        self.points_label.setObjectName("points_label")
        self.points_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.points_label)

        # --- Информационная панель ---
        info_frame = QFrame()
        info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 6, 8, 6)
        info_layout.setSpacing(2)

        self.tab_label = QLabel("Вкладка: —")
        self.tab_label.setObjectName("info_label")
        info_layout.addWidget(self.tab_label)

        self.phase_label = QLabel("Сессия: не начата")
        self.phase_label.setObjectName("info_label")
        info_layout.addWidget(self.phase_label)

        self.speed_label = QLabel("Скорость: —")
        self.speed_label.setObjectName("speed_label")
        info_layout.addWidget(self.speed_label)

        self.earnings_label = QLabel("💰 Сегодня: 0.00 руб. | Всего: 0.00 руб.")
        self.earnings_label.setObjectName("earnings_label")
        info_layout.addWidget(self.earnings_label)

        layout.addWidget(info_frame)

        # --- Прогресс-бар цели ---
        goal_frame = QFrame()
        goal_frame.setObjectName("goal_frame")
        goal_layout = QVBoxLayout(goal_frame)
        goal_layout.setContentsMargins(6, 4, 6, 4)
        goal_layout.setSpacing(2)

        self.goal_label = QLabel("Цель на день: 0 / 0")
        self.goal_label.setObjectName("info_label")
        goal_layout.addWidget(self.goal_label)

        self.goal_bar = QProgressBar()
        self.goal_bar.setObjectName("goal_bar")
        self.goal_bar.setRange(0, 100)
        self.goal_bar.setTextVisible(False)
        goal_layout.addWidget(self.goal_bar)

        # ETA (прогноз времени до цели)
        self.eta_label = QLabel("")
        self.eta_label.setObjectName("info_label")
        goal_layout.addWidget(self.eta_label)

        layout.addWidget(goal_frame)

        # --- Кнопка установки цели ---
        goal_btn = QPushButton("🎯 Установить цель")
        goal_btn.clicked.connect(self._set_goal_dialog)
        goal_btn.setObjectName("goal_btn")
        layout.addWidget(goal_btn)

        # --- Кнопки управления сессией ---
        session_frame = QFrame()
        session_frame.setObjectName("session_frame")
        session_layout = QHBoxLayout(session_frame)
        session_layout.setContentsMargins(4, 4, 4, 4)
        session_layout.setSpacing(8)

        self.start_btn = QPushButton("▶ Старт")
        self.start_btn.clicked.connect(self.logic.start_session)
        self.start_btn.setObjectName("start_btn")
        session_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("■ Стоп")
        self.stop_btn.clicked.connect(self.logic.stop_session)
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setEnabled(False)
        session_layout.addWidget(self.stop_btn)

        # Индикатор статуса
        self.status_indicator = StatusIndicator()
        session_layout.addWidget(self.status_indicator)

        session_layout.addStretch()
        layout.addWidget(session_frame)

        # --- Прогресс-бар спринта ---
        self.sprint_bar = QProgressBar()
        self.sprint_bar.setObjectName("sprint_bar")
        self.sprint_bar.setRange(0, 100)
        self.sprint_bar.setTextVisible(True)
        layout.addWidget(self.sprint_bar)

        # --- Статус сессии ---
        self.session_status = QLabel("")
        self.session_status.setObjectName("info_label")
        layout.addWidget(self.session_status)

    def _create_btn(self, text: str, callback) -> QPushButton:
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setObjectName("icon_btn")
        return btn

    # ---------- Диалоги ----------
    def _set_goal_dialog(self):
        today = time.strftime("%Y-%m-%d")
        current = self.logic.daily_goal
        val, ok = QInputDialog.getInt(
            self,
            "Цель на день",
            f"Установите количество точек на сегодня ({today}):",
            value=current if current > 0 else 100,
            min=0,
            max=10000
        )
        if ok:
            self.logic.set_daily_goal(val)

    def _check_goal_adjustment(self):
        new_goal = self.logic.suggest_goal_adjustment()
        if new_goal is not None:
            reply = QMessageBox.question(
                self,
                "Корректировка цели",
                f"Вы часто перевыполняете цель. Предложить увеличить её до {new_goal} точек?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.logic.set_daily_goal(new_goal)

    # ---------- Открытие окон ----------
    def _show_settings(self):
        from .settings_window import SettingsWindow
        if self.settings_window is None or not self.settings_window.isVisible():
            self.settings_window = SettingsWindow(self.logic, self._on_settings_changed, self)
            self.settings_window.settings_changed.connect(self._on_settings_changed)
            self.settings_window.show()
        else:
            self.settings_window.raise_()

    def _show_stats(self):
        from .stats_window import StatsWindow
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsWindow(self.logic, self)
            self.stats_window.show()
        else:
            self.stats_window.raise_()

    def _show_charts(self):
        from .charts_window import ChartsWindow
        if self.charts_window is None or not self.charts_window.isVisible():
            self.charts_window = ChartsWindow(self.logic, self)
            self.charts_window.show()
        else:
            self.charts_window.raise_()

    def _show_records(self):
        from .records_window import RecordsWindow
        if self.records_window is None or not self.records_window.isVisible():
            self.records_window = RecordsWindow(self.logic, self)
            self.records_window.show()
        else:
            self.records_window.raise_()

    def _toggle_floating(self):
        from .floating_widget import FloatingWidget
        if self.floating_widget is None or not self.floating_widget.isVisible():
            self.floating_widget = FloatingWidget(self.logic)
            self.floating_widget.show()
        else:
            self.floating_widget.close()
            self.floating_widget = None

    def _show_advice(self):
        from core.analytics import Analytics
        recommendations = Analytics.get_recommendations(self.logic)
        
        advice_window = QDialog(self)
        advice_window.setWindowTitle("💡 Умные советы")
        advice_window.setFixedSize(450, 400)
        advice_window.setStyleSheet(ADVICE_STYLE)
        
        layout = QVBoxLayout(advice_window)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = QLabel("💡 Умные советы")
        title.setObjectName("title_label")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        text_widget = QLabel()
        text_widget.setObjectName("advice_text")
        text_widget.setWordWrap(True)
        text_widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        if recommendations:
            text = "\n\n".join(f"• {r}" for r in recommendations)
        else:
            text = "Нет данных для анализа. Продолжай работать! 🚀"
        
        text_widget.setText(text)
        layout.addWidget(text_widget)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(advice_window.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        advice_window.exec_()

    def _show_calendar(self):
        from .calendar_widget import CalendarWidget
        
        calendar_window = QDialog(self)
        calendar_window.setWindowTitle("📅 Календарь активности")
        calendar_window.setFixedSize(400, 380)
        calendar_window.setStyleSheet(BASE_STYLE)
        calendar_window.setWindowFlags(calendar_window.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(calendar_window)
        layout.setContentsMargins(10, 10, 10, 10)
        
        calendar = CalendarWidget(self.logic.sessions)
        layout.addWidget(calendar)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(calendar_window.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        calendar_window.exec_()

    def _on_settings_changed(self):
        self._refresh_all()
        self.save_timer.setInterval(self.logic.auto_save_interval * 1000)

    # ---------- Звук ----------
    def _beep(self, freq: int, duration: int):
        if not self.logic.sound_enabled:
            return
        try:
            import winsound
            winsound.Beep(freq, duration)
        except ImportError:
            pass

    def _level_up_effect(self):
        self._beep(1200, 100)
        import threading
        threading.Timer(0.12, lambda: self._beep(1500, 120)).start()
        # Визуальный эффект при уровне
        self.points_label.setStyleSheet(f"font-size: 50px; font-weight: 700; color: {ACCENT}; background: transparent;")
        QTimer.singleShot(500, lambda: self.points_label.setStyleSheet(f"font-size: 46px; font-weight: 700; color: {FG}; background: transparent;"))

    # ---------- Автосохранение ----------
    def _auto_save(self):
        save_progress(
            self.logic.points,
            self.logic.level,
            self.logic.sprint_duration,
            self.logic.break_duration,
            self.logic.sprint_repeats,
            self.logic.sessions,
            self.logic.session_active,
            self.logic.session_start,
            self.logic.session_points,
            self.logic.tab_times,
            self.logic.daily_goal,
            self.logic.goal_start_date,
            self.logic.records,
            self.logic.current_phase,
            self.logic.current_sprint_index,
            self.logic.sprint_finished,
            self.logic.current_phase_start,
            self.logic.current_tab,
            self.logic._last_tab_poll,
            self.logic._recording,
        )

    # ---------- Обновление интерфейса ----------
    def _refresh_all(self):
        try:
            today_points = self.logic.get_today_points()
            self.points_label.setText(str(today_points))
            self.rank_label.setText(self.logic.get_rank())

            self.start_btn.setEnabled(not self.logic.session_active)
            self.stop_btn.setEnabled(self.logic.session_active)
            self.status_indicator.set_active(self.logic.session_active)

            if self.logic.session_active:
                if self.logic.current_phase == "sprint":
                    self.phase_label.setText(f"Спринт {self.logic.current_sprint_index + 1}/{self.logic.sprint_repeats}")
                    self.phase_label.setStyleSheet(f"color: {ACCENT};")
                elif self.logic.current_phase == "break":
                    self.phase_label.setText(f"Перерыв {self.logic.current_sprint_index + 1}/{self.logic.sprint_repeats}")
                    self.phase_label.setStyleSheet("color: #ffd166;")
                elif self.logic.sprint_finished:
                    self.phase_label.setText("✅ Все спринты завершены!")
                    self.phase_label.setStyleSheet(f"color: {ACCENT};")
                else:
                    self.phase_label.setText("Сессия: идёт")
                    self.phase_label.setStyleSheet(f"color: {ACCENT};")
            else:
                self.phase_label.setText("Сессия: не начата")
                self.phase_label.setStyleSheet("color: #888888;")

            display = self.logic.current_tab if len(self.logic.current_tab) <= 48 else self.logic.current_tab[:45] + "..."
            self.tab_label.setText(f"Вкладка: {display}")

            phase, remaining, progress = self.logic._update_phase_progress()
            self.sprint_bar.setValue(int(progress * 100))
            if phase == "sprint":
                mins, secs = divmod(int(remaining), 60)
                self.sprint_bar.setFormat(f"⏱ Спринт: {mins:02d}:{secs:02d}")
                self.session_status.setText(f"Точки в спринте: {self.logic.session_points}")
            elif phase == "break":
                mins, secs = divmod(int(remaining), 60)
                self.sprint_bar.setFormat(f"⏱ Перерыв: {mins:02d}:{secs:02d}")
                self.session_status.setText(f"Следующий спринт через {mins} мин")
            else:
                self.sprint_bar.setFormat("")
                self.session_status.setText("")

            self._update_speed_label()
            self._update_goal_bar()

            # --- ETA (прогноз времени до цели) ---
            eta_hours = self.logic.get_goal_eta()
            if eta_hours is not None and eta_hours >= 0:
                if eta_hours == 0:
                    eta_text = "Цель достигнута! 🎉"
                else:
                    hours = int(eta_hours)
                    minutes = int((eta_hours - hours) * 60)
                    eta_text = f"Прогноз: ~{hours} ч {minutes} мин"
            else:
                eta_text = ""
            self.eta_label.setText(eta_text)

            today_earn = self.logic.get_today_earnings()
            total_earn = self.logic.get_total_earnings()
            self.earnings_label.setText(
                f"💰 Сегодня: {today_earn:.2f} руб. | Всего: {total_earn:.2f} руб."
            )
        except Exception as e:
            print(f"Ошибка обновления интерфейса: {e}")

    def _update_speed_label(self):
        if self.logic.session_active and self.logic.session_points > 0:
            prod_time = self.logic.get_current_productive_seconds()
            speed = calc_points_per_hour(self.logic.session_points, prod_time)
            if speed is not None:
                self.speed_label.setText(f"⚡ Скорость: {speed:.1f} точ/ч")
                self.speed_label.setStyleSheet(f"color: {ACCENT};")
            else:
                self.speed_label.setText("⚡ Скорость: —")
                self.speed_label.setStyleSheet("color: #888888;")
        else:
            total_points = self.logic.points
            total_prod = 0.0
            for s in self.logic.sessions:
                total_prod += get_productive_tab_time(s.tab_times)
            speed = calc_points_per_hour(total_points, total_prod)
            if speed is not None:
                self.speed_label.setText(f"⚡ Средняя скорость: {speed:.1f} точ/ч")
                self.speed_label.setStyleSheet("color: #888888;")
            else:
                self.speed_label.setText("⚡ Скорость: —")
                self.speed_label.setStyleSheet("color: #888888;")

    def _update_goal_bar(self):
        goal = self.logic.daily_goal
        today_points = self.logic.get_today_points()
        progress = self.logic.get_goal_progress()
        self.goal_bar.setValue(int(progress * 100))
        if goal > 0:
            self.goal_label.setText(
                f"Цель на день: {today_points} / {goal} точек  (выполнено {int(progress*100)}%)"
            )
            if progress >= 1.0:
                self.goal_label.setStyleSheet(f"color: {ACCENT};")
            else:
                self.goal_label.setStyleSheet("color: #888888;")
        else:
            self.goal_label.setText("Цель не установлена")
            self.goal_label.setStyleSheet("color: #888888;")

    # ---------- Анимация ----------
    def _tick(self):
        try:
            today_points = self.logic.get_today_points()

            # Анимация масштаба цифры
            if self.points_scale > 1.0:
                self.points_scale = max(1.0, self.points_scale - 0.035)
            size = int(38 * self.points_scale)
            self.points_label.setStyleSheet(f"font-size: {size}px; font-weight: 700; color: {FG}; background: transparent;")

            # Эффект "всплеска" при новых точках
            if today_points != self._last_today_points:
                self.points_label.setStyleSheet(f"font-size: {int(38 * 1.35)}px; font-weight: 700; color: {ACCENT}; background: transparent;")
                self._last_today_points = today_points
                self.points_scale = 1.35

            self.logic.tick()
        except Exception:
            pass

    # ---------- Закрытие ----------
    def closeEvent(self, event):
        self._auto_save()
        self.logic.close()
        if self.floating_widget is not None:
            self.floating_widget.close()
        event.accept()