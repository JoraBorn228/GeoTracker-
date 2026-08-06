#!/usr/bin/env python3
"""
Трекер продуктивности картографа.
Точка входа (PyQt5).
"""
import sys
import time

from PyQt5.QtWidgets import QApplication

from core.logic import TrackerLogic
from ui.main_window import MainWindow
from storage.storage import load_progress
from storage.settings_manager import load_settings


def main():
    # Загружаем данные
    data = load_progress()
    settings = load_settings()

    logic = TrackerLogic()
    
    # Основные данные
    logic.points = data.get("points", 0)
    logic.level = data.get("level", 1)
    logic.sessions = data.get("sessions", [])
    logic.daily_goal = data.get("daily_goal", 0)
    logic.goal_start_date = data.get("goal_start_date", time.strftime("%Y-%m-%d"))
    logic.records = data.get("records", {
        "max_points_per_day": 0,
        "max_points_per_sprint": 0,
        "max_speed_per_session": 0.0,
        "max_speed_per_day": 0.0,
    })

    # Настройки
    logic.sprint_duration = settings.get("sprint_duration", 15)
    logic.break_duration = settings.get("break_duration", 5)
    logic.sprint_repeats = settings.get("sprint_repeats", 1)
    logic.point_price = settings.get("point_price", 1.3)
    logic.auto_save_interval = settings.get("auto_save_interval", 60)
    logic.sound_enabled = settings.get("sound_enabled", True)
    logic.auto_goal_adjustment = settings.get("auto_goal_adjustment", True)

    # --- Восстановление активной сессии ---
    active = data.get("active_session")
    if active and active.get("active", False):
        logic.session_active = True
        logic.session_start = active.get("started_at")
        logic.session_points = active.get("points", 0)
        logic.tab_times = active.get("tab_times", {})
        logic.current_phase = active.get("current_phase", "idle")
        logic.current_sprint_index = active.get("current_sprint_index", 0)
        logic.sprint_finished = active.get("sprint_finished", False)
        logic.current_phase_start = active.get("phase_start")
        logic.current_tab = active.get("current_tab", "")
        logic._last_tab_poll = active.get("last_tab_poll", time.time())
        logic._recording = active.get("recording", False)
        
        # Если есть текущая фаза, восстанавливаем её
        if logic.current_phase == "sprint":
            logic._recording = True

    # Создаём Qt-приложение
    app = QApplication(sys.argv)
    window = MainWindow(logic)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()