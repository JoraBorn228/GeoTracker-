"""
Стили для всех окон приложения.
"""

# Базовый стиль для всего приложения
BASE_STYLE = """
    QMainWindow, QWidget {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
        font-weight: 500;
    }
"""

# Стиль для главного окна
MAIN_STYLE = """
    QMainWindow, QWidget#central {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
        font-weight: 500;
    }
    QFrame#top_frame {
        background-color: transparent;
        border: none;
    }
    QFrame#info_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
        padding: 4px;
    }
    QFrame#goal_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
        padding: 4px;
    }
    QFrame#session_frame {
        background-color: transparent;
        border: none;
    }
    QLabel {
        color: #eaeaea;
        font-weight: 500;
    }
    #rank_label {
        font-size: 15px;
        font-weight: 700;
        color: #ff6b6b;
        padding: 4px 8px;
    }
    #points_label {
        font-size: 46px;
        font-weight: 700;
        color: #eaeaea;
        padding: 6px 0;
        background-color: transparent;
    }
    #info_label {
        font-size: 11px;
        font-weight: 500;
        color: #888888;
        padding: 0 4px;
    }
    #speed_label {
        font-size: 11px;
        font-weight: 600;
        color: #00d4aa;
        padding: 0 4px;
    }
    #earnings_label {
        font-size: 11px;
        font-weight: 600;
        color: #ffd700;
        padding: 0 4px;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 14px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    QPushButton:pressed {
        background-color: #1a1a3e;
    }
    QPushButton:disabled {
        background-color: #2a2a3a;
        color: #666;
    }
    #icon_btn {
        background-color: transparent;
        border: none;
        font-size: 18px;
        padding: 4px 6px;
        font-weight: 400;
    }
    #icon_btn:hover {
        background-color: #2a2a40;
        border-radius: 4px;
    }
    #start_btn {
        background-color: #00d4aa;
        color: #15152a;
        border: none;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 700;
    }
    #start_btn:hover {
        background-color: #00b894;
    }
    #start_btn:disabled {
        background-color: #2a2a3a;
        color: #666;
    }
    #stop_btn {
        background-color: #ff6b6b;
        color: #eaeaea;
        border: none;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 700;
    }
    #stop_btn:hover {
        background-color: #e05555;
    }
    #stop_btn:disabled {
        background-color: #2a2a3a;
        color: #666;
    }
    #goal_btn {
        background-color: #2a2a40;
        border: 1px solid #2a2a5e;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 600;
    }
    #goal_btn:hover {
        background-color: #3a3a5e;
        border-color: #00d4aa;
    }
    #goal_bar {
        background-color: #2a2a40;
        border: none;
        border-radius: 4px;
        height: 8px;
    }
    #goal_bar::chunk {
        background-color: #ffd166;
        border-radius: 4px;
    }
    #sprint_bar {
        background-color: #2a2a40;
        border: none;
        border-radius: 4px;
        height: 12px;
    }
    #sprint_bar::chunk {
        background-color: #00d4aa;
        border-radius: 4px;
    }
    QProgressBar {
        text-align: center;
        color: #eaeaea;
        font-size: 10px;
        font-weight: 600;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
"""

# Стиль для окна настроек
SETTINGS_STYLE = """
    QDialog {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
    }
    QLabel {
        color: #eaeaea;
    }
    QLineEdit {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 10px;
        font-size: 11px;
    }
    QLineEdit:focus {
        border-color: #00d4aa;
    }
    QComboBox {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 11px;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox:hover {
        border-color: #00d4aa;
    }
    QComboBox QAbstractItemView {
        background-color: #2a2a40;
        color: #eaeaea;
        selection-background-color: #00d4aa;
        selection-color: #15152a;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
    }
    QCheckBox {
        color: #eaeaea;
        font-size: 11px;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #2a2a40;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
    }
    QCheckBox::indicator:checked {
        background-color: #00d4aa;
        border-color: #00d4aa;
    }
    QGroupBox {
        color: #00d4aa;
        font-weight: 600;
        font-size: 11px;
        border: 1px solid #2a2a5e;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 8px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #save_btn {
        background-color: #00d4aa;
        color: #15152a;
        border: none;
        padding: 8px 25px;
    }
    #save_btn:hover {
        background-color: #00b894;
    }
    #reset_btn {
        background-color: #6b2a2a;
        color: #eaeaea;
        border: none;
        padding: 8px 25px;
    }
    #reset_btn:hover {
        background-color: #8a3333;
    }
    #settings_title {
        font-size: 16px;
        font-weight: 700;
        color: #00d4aa;
        padding-bottom: 5px;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    QScrollArea {
        background: transparent;
        border: none;
    }
    #settings_container {
        background: transparent;
    }
"""

# Стиль для окна статистики
STATS_STYLE = """
    QDialog {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
        font-weight: 500;
    }
    QLabel {
        color: #eaeaea;
        font-weight: 500;
    }
    QLineEdit {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 8px;
        font-size: 11px;
        font-weight: 500;
    }
    QLineEdit:focus {
        border-color: #00d4aa;
    }
    QComboBox {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 11px;
        font-weight: 500;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox:hover {
        border-color: #00d4aa;
    }
    QComboBox QAbstractItemView {
        background-color: #2a2a40;
        color: #eaeaea;
        selection-background-color: #00d4aa;
        selection-color: #15152a;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        font-weight: 500;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 14px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #quick_btn {
        background-color: #1a1a3e;
        border: 1px solid #2a2a5e;
        padding: 4px 12px;
        font-size: 10px;
        font-weight: 500;
    }
    #quick_btn:hover {
        background-color: #00d4aa;
        color: #15152a;
        border-color: #00d4aa;
    }
    #filter_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
    }
    #apply_btn {
        background-color: #00d4aa;
        color: #15152a;
        border: none;
        padding: 6px 12px;
        font-weight: 700;
    }
    #apply_btn:hover {
        background-color: #00b894;
    }
    #refresh_btn {
        background-color: transparent;
        border: none;
        font-size: 16px;
    }
    #refresh_btn:hover {
        background-color: #2a2a40;
        border-radius: 4px;
    }
    #stats_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
    }
    #stats_label {
        font-size: 11px;
        font-weight: 500;
        color: #eaeaea;
        background-color: transparent;
        padding: 4px 8px;
    }
    #quick_label {
        font-weight: 700;
        color: #888;
        font-size: 10px;
    }
    #left_frame {
        background-color: transparent;
    }
    #right_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
    }
    #detail_title {
        font-size: 14px;
        font-weight: 700;
        color: #00d4aa;
        padding-bottom: 4px;
        background-color: transparent;
    }
    #detail_text {
        background-color: #12122a;
        color: #eaeaea;
        border: 1px solid #2a2a5e;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        padding: 8px;
    }
    #delete_btn {
        background-color: #6b2a2a;
        color: #eaeaea;
        border: none;
        margin-top: 8px;
        font-weight: 600;
    }
    #delete_btn:hover {
        background-color: #8a3333;
    }
    #delete_btn:disabled {
        background-color: #2a2a3a;
        color: #666;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    QScrollArea {
        background: transparent;
        border: none;
    }
    #card_container {
        background: transparent;
    }
    #card {
        background-color: #1a1a3e;
        border: 1px solid #2a2a5e;
        border-radius: 6px;
        padding: 8px;
    }
    #card:hover {
        background-color: #22225a;
        border-color: #3d3d7b;
    }
    #card_points {
        color: #00d4aa;
        font-weight: 700;
        font-size: 14px;
    }
    #card_date {
        color: #aaa;
        font-size: 11px;
        font-weight: 500;
    }
    #card_stats {
        color: #888;
        font-size: 10px;
        font-weight: 500;
    }
"""

# Стиль для окна рекордов
RECORDS_STYLE = """
    QDialog {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
    }
    #records_title {
        font-size: 16px;
        font-weight: 700;
        color: #00d4aa;
    }
    #record_card {
        background-color: #1a1a3e;
        border: 1px solid #2a2a5e;
        border-radius: 6px;
        padding: 4px;
    }
    #record_card:hover {
        background-color: #22225a;
        border-color: #3d3d7b;
    }
    #record_title {
        font-size: 10px;
        font-weight: 500;
        color: #eaeaea;
    }
    #record_value {
        font-size: 16px;
        font-weight: 700;
    }
    #record_unit {
        font-size: 10px;
        color: #888888;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    QScrollArea {
        background: transparent;
        border: none;
    }
"""

# Стиль для окна графиков
CHARTS_STYLE = """
    QDialog {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
        font-size: 11px;
    }
    QLabel {
        color: #eaeaea;
    }
    QCheckBox {
        color: #eaeaea;
        font-size: 11px;
        font-weight: 500;
        spacing: 6px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        background-color: #2a2a40;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
    }
    QCheckBox::indicator:checked {
        background-color: #00d4aa;
        border-color: #00d4aa;
    }
    QCheckBox::indicator:hover {
        border-color: #00d4aa;
    }
    QFrame#settings_frame {
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #charts_title {
        font-size: 14px;
        font-weight: 700;
        color: #00d4aa;
    }
    #status_label {
        font-size: 10px;
        color: #888888;
        padding: 4px 8px;
        background-color: #1a1a3e;
        border-radius: 4px;
        border: 1px solid #2a2a5e;
    }
"""

# Стиль для плавающего виджета
FLOATING_STYLE = """
    QFrame#main_frame {
        background-color: rgba(21, 21, 42, 220);
        border: 1px solid #2a2a5e;
        border-radius: 8px;
    }
    QLabel {
        color: #eaeaea;
        font-family: "Segoe UI";
        background-color: transparent;
    }
    #speed_label {
        font-size: 13px;
        font-weight: 700;
        color: #00d4aa;
    }
    #time_label {
        font-size: 11px;
        font-weight: 500;
        color: #888888;
    }
"""

# Стиль для окна советов
ADVICE_STYLE = """
    QDialog {
        background-color: #15152a;
        color: #eaeaea;
        font-family: "Segoe UI";
    }
    QLabel {
        color: #eaeaea;
    }
    QPushButton {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    QPushButton:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #close_btn {
        background-color: #2a2a40;
        color: #eaeaea;
        border: 1px solid #3d3d6b;
        border-radius: 4px;
        padding: 6px 20px;
        font-size: 11px;
        font-weight: 600;
    }
    #close_btn:hover {
        background-color: #3d3d6b;
        border-color: #00d4aa;
    }
    #title_label {
        font-size: 16px;
        font-weight: 700;
        color: #00d4aa;
        padding: 10px;
    }
    #advice_text {
        font-size: 12px;
        padding: 10px;
        background-color: #1a1a3e;
        border-radius: 6px;
        border: 1px solid #2a2a5e;
    }
"""