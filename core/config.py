"""
Глобальные константы и настройки приложения.
"""
import sys
from pathlib import Path

# Определяем корневую папку
if getattr(sys, 'frozen', False):
    # Запуск из .exe
    ROOT_DIR = Path(sys.executable).parent
else:
    # Запуск из Python
    ROOT_DIR = Path(__file__).parent.parent

# --- Файлы данных ---
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SAVE_FILE = DATA_DIR / "progress.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# --- Размеры окна ---
WINDOW_W = 420
WINDOW_H = 420

# --- Маркеры для определения продуктивной вкладки ---
PRODUCTIVE_TAB_MARKERS = ("бекофис", "бэкофис", "backoffice", "яндекс", "yandex")

# --- Настройки спринтов (доступные значения для выпадающих списков) ---
SPRINT_DURATIONS = (5, 10, 15, 20, 25, 30, 45, 60)
BREAK_DURATIONS = (1, 2, 3, 5, 10, 15)
REPEAT_OPTIONS = list(range(1, 11))

# --- Звания (по накопленным очкам) ---
RANKS = {
    0: "Стажёр",
    100: "Картограф",
    500: "Эксперт",
    1000: "Мастер",
    5000: "Гуру",
    10000: "Легенда"
}

# --- Цветовая схема ---
BG = "#1a1a2e"
BG_FLASH = "#3d3d6b"
FG = "#eaeaea"
ACCENT = "#00d4aa"
LEVEL_COLOR = "#ff6b6b"
BAR_BG = "#2a2a40"
BAR_FG = "#00d4aa"
GOAL_BAR_FG = "#ffd166"
BTN_BG = "#2a2a40"
BTN_ACTIVE = "#00d4aa"
BTN_STOP = "#ff6b6b"
PARTICLE_COLORS = ("#00d4aa", "#ffd166", "#ff6b6b", "#4ecdc4", "#a29bfe")

# --- Суффиксы браузеров для парсинга заголовка окна ---
BROWSER_SUFFIXES = (
    " - Google Chrome",
    " — Google Chrome",
    " - Mozilla Firefox",
    " — Mozilla Firefox",
    " - Microsoft Edge",
    " — Microsoft Edge",
    " - Opera",
    " - Brave",
    " - Yandex",
    " - Vivaldi",
)