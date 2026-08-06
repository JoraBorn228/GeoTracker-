"""
Окно настроек приложения на PyQt5 (с ручным вводом чисел).
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QMessageBox, QWidget,
    QScrollArea, QFrame, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from core.config import BG, FG, ACCENT, BTN_BG, BTN_ACTIVE, BAR_BG
from storage.settings_manager import load_settings, save_settings, DEFAULT_SETTINGS
from ui.styles import SETTINGS_STYLE


class SettingsWindow(QDialog):
    settings_changed = pyqtSignal()

    def __init__(self, logic, on_settings_changed=None, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.on_settings_changed = on_settings_changed

        self.settings = load_settings()

        self.setWindowTitle("⚙️ Настройки")
        self.setFixedSize(550, 600)
        self.setStyleSheet(SETTINGS_STYLE)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Заголовок
        title = QLabel("⚙️ Настройки приложения")
        title.setObjectName("settings_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Скролл-область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setObjectName("settings_container")
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # ---- Секция: Спринты (с ручным вводом) ----
        sprint_group = self._create_group("⏱ Настройки спринтов")
        sprint_layout = QGridLayout(sprint_group)
        sprint_layout.setVerticalSpacing(8)
        sprint_layout.setHorizontalSpacing(15)

        # Длительность спринта
        sprint_layout.addWidget(QLabel("Длительность спринта:"), 0, 0)
        self.sprint_combo = QComboBox()
        self.sprint_combo.setEditable(True)  # Разрешаем ручной ввод
        self.sprint_combo.addItems([str(d) for d in [5, 10, 15, 20, 25, 30, 45, 60]])
        self.sprint_combo.setCurrentText(str(self.settings.get("sprint_duration", 15)))
        self.sprint_combo.setFixedWidth(100)
        self.sprint_combo.setToolTip("Введите число от 1 до 120 или выберите из списка")
        sprint_layout.addWidget(self.sprint_combo, 0, 1)
        sprint_layout.addWidget(QLabel("мин"), 0, 2)

        # Длительность перерыва
        sprint_layout.addWidget(QLabel("Длительность перерыва:"), 1, 0)
        self.break_combo = QComboBox()
        self.break_combo.setEditable(True)
        self.break_combo.addItems([str(d) for d in [1, 2, 3, 5, 10, 15]])
        self.break_combo.setCurrentText(str(self.settings.get("break_duration", 5)))
        self.break_combo.setFixedWidth(100)
        self.break_combo.setToolTip("Введите число от 0 до 30 или выберите из списка")
        sprint_layout.addWidget(self.break_combo, 1, 1)
        sprint_layout.addWidget(QLabel("мин"), 1, 2)

        # Количество повторов
        sprint_layout.addWidget(QLabel("Количество повторов:"), 2, 0)
        self.repeats_combo = QComboBox()
        self.repeats_combo.setEditable(True)
        self.repeats_combo.addItems([str(r) for r in range(1, 11)])
        self.repeats_combo.setCurrentText(str(self.settings.get("sprint_repeats", 1)))
        self.repeats_combo.setFixedWidth(100)
        self.repeats_combo.setToolTip("Введите число от 1 до 20 или выберите из списка")
        sprint_layout.addWidget(self.repeats_combo, 2, 1)
        sprint_layout.addWidget(QLabel("раз"), 2, 2)

        # Подсказка о допустимых значениях
        hint_label = QLabel("💡 Можно ввести своё значение в поле")
        hint_label.setStyleSheet("color: #666; font-size: 9px; font-style: italic;")
        sprint_layout.addWidget(hint_label, 3, 0, 1, 3)

        sprint_layout.setColumnStretch(3, 1)
        scroll_layout.addWidget(sprint_group)

        # ---- Секция: Цель ----
        goal_group = self._create_group("🎯 Настройки цели")
        goal_layout = QGridLayout(goal_group)
        goal_layout.setVerticalSpacing(8)
        goal_layout.setHorizontalSpacing(15)

        goal_layout.addWidget(QLabel("Автокорректировка цели:"), 0, 0)
        self.auto_goal_check = QCheckBox()
        self.auto_goal_check.setChecked(self.settings.get("auto_goal_adjustment", True))
        goal_layout.addWidget(self.auto_goal_check, 0, 1)
        goal_layout.addWidget(QLabel("Предлагать увеличить цель при перевыполнении"), 0, 2)

        goal_layout.setColumnStretch(3, 1)
        scroll_layout.addWidget(goal_group)

        # ---- Секция: Заработок ----
        money_group = self._create_group("💰 Настройки заработка")
        money_layout = QGridLayout(money_group)
        money_layout.setVerticalSpacing(8)
        money_layout.setHorizontalSpacing(15)

        money_layout.addWidget(QLabel("Цена одной точки:"), 0, 0)
        self.price_edit = QLineEdit()
        self.price_edit.setText(str(self.settings.get("point_price", 1.3)))
        self.price_edit.setFixedWidth(100)
        self.price_edit.setToolTip("Введите число (например, 1.5)")
        money_layout.addWidget(self.price_edit, 0, 1)
        money_layout.addWidget(QLabel("руб."), 0, 2)

        money_layout.setColumnStretch(3, 1)
        scroll_layout.addWidget(money_group)

        # ---- Секция: Система ----
        system_group = self._create_group("🖥 Системные настройки")
        system_layout = QGridLayout(system_group)
        system_layout.setVerticalSpacing(8)
        system_layout.setHorizontalSpacing(15)

        system_layout.addWidget(QLabel("Интервал автосохранения:"), 0, 0)
        self.save_edit = QLineEdit()
        self.save_edit.setText(str(self.settings.get("auto_save_interval", 60)))
        self.save_edit.setFixedWidth(100)
        self.save_edit.setToolTip("Введите число от 10 до 600")
        system_layout.addWidget(self.save_edit, 0, 1)
        system_layout.addWidget(QLabel("сек"), 0, 2)

        system_layout.addWidget(QLabel("Включить звуки:"), 1, 0)
        self.sound_check = QCheckBox()
        self.sound_check.setChecked(self.settings.get("sound_enabled", True))
        system_layout.addWidget(self.sound_check, 1, 1)

        system_layout.setColumnStretch(3, 1)
        scroll_layout.addWidget(system_group)

        # ---- Секция: О приложении ----
        about_group = self._create_group("📌 О приложении")
        about_layout = QVBoxLayout(about_group)
        about_layout.setSpacing(4)

        about_label = QLabel(
            "Картограф v2.0\n"
            "Умный трекер продуктивности для картографов\n"
            "© 2026"
        )
        about_label.setAlignment(Qt.AlignCenter)
        about_label.setStyleSheet("color: #888; font-size: 10px; line-height: 1.6;")
        about_layout.addWidget(about_label)

        scroll_layout.addWidget(about_group)

        # Растяжка
        scroll_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # ---- Кнопки ----
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setObjectName("save_btn")

        reset_btn = QPushButton("🔄 Сбросить")
        reset_btn.clicked.connect(self._reset_defaults)
        reset_btn.setObjectName("reset_btn")

        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _create_group(self, title: str) -> QGroupBox:
        """Создать группу с заголовком."""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {ACCENT};
                font-weight: 600;
                font-size: 11px;
                border: 1px solid #2a2a5e;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: {ACCENT};
            }}
        """)
        return group

    # ---------- Логика ----------
    def _save_settings(self):
        try:
            # Получаем значения из комбобоксов (поддерживаем ручной ввод)
            sprint_text = self.sprint_combo.currentText().strip()
            break_text = self.break_combo.currentText().strip()
            repeats_text = self.repeats_combo.currentText().strip()

            # Проверяем, что введены числа
            sprint_val = int(sprint_text)
            break_val = int(break_text)
            repeats_val = int(repeats_text)

            # Валидация
            if sprint_val <= 0 or sprint_val > 120:
                raise ValueError("Длительность спринта должна быть от 1 до 120 минут")
            if break_val < 0 or break_val > 30:
                raise ValueError("Длительность перерыва должна быть от 0 до 30 минут")
            if repeats_val < 1 or repeats_val > 20:
                raise ValueError("Количество повторов должно быть от 1 до 20")

            price_val = float(self.price_edit.text().strip())
            if price_val <= 0:
                raise ValueError("Цена точки должна быть > 0")

            save_val = int(self.save_edit.text().strip())
            if save_val < 10 or save_val > 600:
                raise ValueError("Интервал автосохранения должен быть от 10 до 600 секунд")

            new_settings = {
                "sprint_duration": sprint_val,
                "break_duration": break_val,
                "sprint_repeats": repeats_val,
                "point_price": price_val,
                "auto_save_interval": save_val,
                "sound_enabled": self.sound_check.isChecked(),
                "auto_goal_adjustment": self.auto_goal_check.isChecked(),
            }

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return

        save_settings(new_settings)

        self.logic.sprint_duration = new_settings["sprint_duration"]
        self.logic.break_duration = new_settings["break_duration"]
        self.logic.sprint_repeats = new_settings["sprint_repeats"]
        self.logic.point_price = new_settings["point_price"]
        self.logic.auto_save_interval = new_settings["auto_save_interval"]
        self.logic.sound_enabled = new_settings["sound_enabled"]
        self.logic.auto_goal_adjustment = new_settings["auto_goal_adjustment"]

        self.settings_changed.emit()
        if self.on_settings_changed:
            self.on_settings_changed()

        QMessageBox.information(self, "Успех", "Настройки сохранены!")
        self.accept()

    def _reset_defaults(self):
        reply = QMessageBox.question(
            self,
            "Сброс",
            "Сбросить все настройки к стандартным?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.sprint_combo.setCurrentText(str(DEFAULT_SETTINGS["sprint_duration"]))
            self.break_combo.setCurrentText(str(DEFAULT_SETTINGS["break_duration"]))
            self.repeats_combo.setCurrentText(str(DEFAULT_SETTINGS["sprint_repeats"]))
            self.price_edit.setText(str(DEFAULT_SETTINGS["point_price"]))
            self.save_edit.setText(str(DEFAULT_SETTINGS["auto_save_interval"]))
            self.sound_check.setChecked(DEFAULT_SETTINGS["sound_enabled"])
            self.auto_goal_check.setChecked(DEFAULT_SETTINGS["auto_goal_adjustment"])
            QMessageBox.information(self, "Готово", "Настройки сброшены к стандартным")