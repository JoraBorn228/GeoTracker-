"""
Окно графиков на PyQt5 с интеграцией matplotlib.
Настраиваемые графики: точки, заработок, время работы, накопленный итог.
С подсказками при наведении на столбцы.
"""
import time
from typing import List, Dict, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QFrame, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ui.styles import CHARTS_STYLE
from core.models import Session
from core.utils import get_productive_tab_time
from core.config import BG, FG, ACCENT, BAR_BG, BTN_BG


class ChartsWindow(QDialog):
    def __init__(self, logic, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.setStyleSheet(CHARTS_STYLE)
        self.point_price = logic.point_price
        self.daily_data = self._aggregate_daily_data()

        # Храним ссылки на элементы графика для подсказок
        self.bars = []
        self.annotations = []
        self.hover_annotation = None

        self.setWindowTitle("📈 Графики продуктивности")
        self.setGeometry(100, 100, 900, 700)

        self._build_ui()
        self._update_chart()

    # ---------- Интерфейс ----------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Настройка отображения графиков")
        title.setObjectName("charts_title")
        layout.addWidget(title)

        settings_frame = QFrame()
        settings_frame.setObjectName("settings_frame")
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(10, 8, 10, 8)
        settings_layout.setSpacing(15)

        self.show_points = QCheckBox("📌 Точки")
        self.show_points.setChecked(True)
        self.show_points.stateChanged.connect(self._update_chart)

        self.show_money = QCheckBox("💰 Заработок (руб.)")
        self.show_money.setChecked(True)
        self.show_money.stateChanged.connect(self._update_chart)

        self.show_hours = QCheckBox("⏱ Время работы (ч)")
        self.show_hours.setChecked(True)
        self.show_hours.stateChanged.connect(self._update_chart)

        self.show_cumulative = QCheckBox("📈 Накопленный итог")
        self.show_cumulative.setChecked(False)
        self.show_cumulative.stateChanged.connect(self._update_chart)

        settings_layout.addWidget(self.show_points)
        settings_layout.addWidget(self.show_money)
        settings_layout.addWidget(self.show_hours)
        settings_layout.addWidget(self.show_cumulative)
        settings_layout.addStretch()

        layout.addWidget(settings_frame)

        self.figure = Figure(figsize=(8, 5), dpi=100, facecolor="#15152a")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(500)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        # Подсказка в статусной строке (нижняя часть)
        self.status_label = QLabel("Наведите курсор на столбец для просмотра значения")
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)

        btn_frame = QHBoxLayout()
        btn_frame.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        close_btn.setObjectName("close_btn")
        btn_frame.addWidget(close_btn)

        layout.addLayout(btn_frame)
        
    # ---------- Данные ----------
    def _aggregate_daily_data(self) -> Dict[str, Dict]:
        daily = {}
        today = time.strftime("%Y-%m-%d")

        for sess in self.logic.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            if day not in daily:
                daily[day] = {'points': 0, 'money': 0.0, 'hours': 0.0}
            daily[day]['points'] += sess.points
            daily[day]['money'] += sess.points * self.point_price
            daily[day]['hours'] += get_productive_tab_time(sess.tab_times) / 3600.0

        if self.logic.session_active and self.logic.session_points > 0:
            if today not in daily:
                daily[today] = {'points': 0, 'money': 0.0, 'hours': 0.0}
            daily[today]['points'] += self.logic.session_points
            daily[today]['money'] += self.logic.session_points * self.point_price

        return daily

    # ---------- Обновление графика ----------
    def _update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Очищаем старые данные
        self.bars = []
        self.annotations = []

        if not self.daily_data:
            ax.text(0.5, 0.5, "Нет данных для отображения", 
                    ha='center', va='center', color='white', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#15152a')
            self.canvas.draw()
            return

        dates = sorted(self.daily_data.keys())
        x = list(range(len(dates)))

        points_vals = [self.daily_data[d]['points'] for d in dates]
        money_vals = [self.daily_data[d]['money'] for d in dates]
        hours_vals = [self.daily_data[d]['hours'] for d in dates]

        if self.show_cumulative.isChecked():
            cum_points = []
            cum_money = []
            cum_hours = []
            p = m = h = 0
            for i in range(len(dates)):
                p += points_vals[i]
                m += money_vals[i]
                h += hours_vals[i]
                cum_points.append(p)
                cum_money.append(m)
                cum_hours.append(h)
            points_vals = cum_points
            money_vals = cum_money
            hours_vals = cum_hours

        width = 0.25
        colors = {'points': '#00d4aa', 'money': '#ffd700', 'hours': '#ff6b6b'}
        labels = {'points': 'Точки', 'money': 'Заработок (руб.)', 'hours': 'Время (ч)'}
        formats = {'points': '{:.0f}', 'money': '{:.2f} руб.', 'hours': '{:.2f} ч'}

        plotted = False

        # Сохраняем данные для подсказок
        self.bar_data = []

        if self.show_points.isChecked():
            bars = ax.bar([i - width for i in x], points_vals, width, 
                          color=colors['points'], label=labels['points'], alpha=0.85)
            self.bars.extend(bars)
            self.bar_data.extend([{'type': 'points', 'value': v, 'date': dates[i]} for i, v in enumerate(points_vals)])
            plotted = True

        if self.show_money.isChecked():
            bars = ax.bar(x, money_vals, width, 
                          color=colors['money'], label=labels['money'], alpha=0.85)
            self.bars.extend(bars)
            self.bar_data.extend([{'type': 'money', 'value': v, 'date': dates[i]} for i, v in enumerate(money_vals)])
            plotted = True

        if self.show_hours.isChecked():
            bars = ax.bar([i + width for i in x], hours_vals, width, 
                          color=colors['hours'], label=labels['hours'], alpha=0.85)
            self.bars.extend(bars)
            self.bar_data.extend([{'type': 'hours', 'value': v, 'date': dates[i]} for i, v in enumerate(hours_vals)])
            plotted = True

        if not plotted:
            ax.text(0.5, 0.5, "Выберите хотя бы одну метрику", 
                    ha='center', va='center', color='white', fontsize=14, transform=ax.transAxes)
            ax.set_facecolor('#15152a')
            self.canvas.draw()
            return

        # Настройки оформления
        ax.set_title(
            "Продуктивность по дням" + (" (накопленный итог)" if self.show_cumulative.isChecked() else ""),
            color='white', fontsize=14, fontweight='bold'
        )
        ax.set_xlabel("Дата", color='white', fontsize=11)
        ax.set_ylabel("Значение", color='white', fontsize=11)
        ax.tick_params(colors='white', labelsize=9)
        ax.grid(True, color='#2a2a40', linestyle='--', alpha=0.5, axis='y')
        ax.set_facecolor('#15152a')

        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right', color='white', fontsize=9)

        ax.legend(loc='upper left', facecolor='#1a1a3e', labelcolor='white', 
                  edgecolor='#2a2a5e', fontsize=10)

        ax.relim()
        ax.autoscale_view()

        self.figure.tight_layout()
        self.canvas.draw()

        # Подключаем событие движения мыши
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        self.canvas.mpl_connect('axes_leave_event', self._on_leave)

    # ---------- Подсказки при наведении ----------
    def _on_hover(self, event):
        """Обработчик наведения мыши на график."""
        if event.inaxes is None:
            return

        # Ищем, над каким столбцом курсор
        for bar, data in zip(self.bars, self.bar_data):
            if bar.contains(event)[0]:
                # Форматируем значение
                value = data['value']
                date = data['date']
                if data['type'] == 'points':
                    display_value = f"{value:.0f}"
                    unit = "точек"
                elif data['type'] == 'money':
                    display_value = f"{value:.2f}"
                    unit = "руб."
                else:  # hours
                    display_value = f"{value:.2f}"
                    unit = "ч"

                # Обновляем статусную строку
                self.status_label.setText(
                    f"📅 {date} — {display_value} {unit} ({data['type']})"
                )

                # Показываем аннотацию над столбцом
                if self.hover_annotation is not None:
                    self.hover_annotation.remove()
                    self.hover_annotation = None

                self.hover_annotation = event.inaxes.annotate(
                    display_value,
                    xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 5),
                    textcoords='offset points',
                    ha='center',
                    va='bottom',
                    color='white',
                    fontsize=10,
                    fontweight='bold',
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor='#1a1a3e',
                        edgecolor=bar.get_facecolor(),
                        alpha=0.9
                    )
                )
                self.canvas.draw_idle()
                return

        # Если ни один столбец не найден — убираем аннотацию
        if self.hover_annotation is not None:
            self.hover_annotation.remove()
            self.hover_annotation = None
            self.status_label.setText("Наведите курсор на столбец для просмотра значения")
            self.canvas.draw_idle()

    def _on_leave(self, event):
        """Обработчик ухода курсора с графика."""
        if self.hover_annotation is not None:
            self.hover_annotation.remove()
            self.hover_annotation = None
            self.status_label.setText("Наведите курсор на столбец для просмотра значения")
            self.canvas.draw_idle()