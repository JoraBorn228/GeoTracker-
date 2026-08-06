"""
Окно статистики на PyQt5 с улучшенным стилем.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget, QMessageBox, QComboBox,
    QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor

import time
from datetime import datetime, timedelta
from typing import List, Optional

from ui.styles import STATS_STYLE
from core.models import Session
from core.utils import (
    format_duration, format_datetime, format_points_per_hour,
    is_productive_tab, get_productive_tab_time,
    calc_points_per_hour, calc_level,
)
from core.config import BG, FG, ACCENT, BAR_BG, BTN_BG, BTN_STOP
from storage.storage import save_progress


class StatsWindow(QDialog):
    def __init__(self, logic, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.setStyleSheet(STATS_STYLE)
        self.selected_session: Optional[Session] = None
        self.filtered_sessions: List[Session] = []
        self.card_frames: List[QFrame] = []

        self.setWindowTitle("📊 Статистика сессий")
        self.setGeometry(100, 100, 1000, 800)

        self._build_ui()
        self._apply_filter()

    # ---------- Интерфейс ----------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # --- Верхняя панель с быстрыми кнопками ---
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(6)

        quick_label = QLabel("📅 Быстрый выбор:")
        quick_label.setObjectName("quick_label")
        quick_layout.addWidget(quick_label)

        self.btn_today = self._create_quick_btn("Сегодня", lambda: self._set_quick_date(0))
        self.btn_yesterday = self._create_quick_btn("Вчера", lambda: self._set_quick_date(1))
        self.btn_week = self._create_quick_btn("Неделя", lambda: self._set_quick_date(7))
        self.btn_month = self._create_quick_btn("Месяц", lambda: self._set_quick_date(30))
        self.btn_all = self._create_quick_btn("Всё время", self._set_all_time)

        quick_layout.addWidget(self.btn_today)
        quick_layout.addWidget(self.btn_yesterday)
        quick_layout.addWidget(self.btn_week)
        quick_layout.addWidget(self.btn_month)
        quick_layout.addWidget(self.btn_all)
        quick_layout.addStretch()

        layout.addLayout(quick_layout)

        # --- Панель фильтрации и сортировки ---
        filter_frame = QFrame()
        filter_frame.setObjectName("filter_frame")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(8, 6, 8, 6)
        filter_layout.setSpacing(10)

        filter_layout.addWidget(QLabel("От:"))
        self.filter_from = QLineEdit()
        self.filter_from.setPlaceholderText("ГГГГ-ММ-ДД")
        self.filter_from.setFixedWidth(110)
        filter_layout.addWidget(self.filter_from)

        filter_layout.addWidget(QLabel("До:"))
        self.filter_to = QLineEdit()
        self.filter_to.setPlaceholderText("ГГГГ-ММ-ДД")
        self.filter_to.setFixedWidth(110)
        filter_layout.addWidget(self.filter_to)

        apply_btn = QPushButton("🔍 Применить")
        apply_btn.clicked.connect(self._apply_filter)
        apply_btn.setObjectName("apply_btn")
        filter_layout.addWidget(apply_btn)

        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "📅 по дате (новые)", "📅 по дате (старые)",
            "📈 по точкам (↑)", "📈 по точкам (↓)",
            "⚡ по скорости (↑)", "⚡ по скорости (↓)"
        ])
        self.sort_combo.currentTextChanged.connect(self._apply_filter)
        self.sort_combo.setFixedWidth(160)
        filter_layout.addWidget(self.sort_combo)

        refresh_btn = QPushButton("🔄")
        refresh_btn.clicked.connect(self._apply_filter)
        refresh_btn.setFixedWidth(30)
        refresh_btn.setObjectName("refresh_btn")
        filter_layout.addWidget(refresh_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # --- Блок агрегированной статистики ---
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("stats_frame")
        stats_layout = QVBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(12, 8, 12, 8)
        
        self.stats_label = QLabel("")
        self.stats_label.setObjectName("stats_label")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(self.stats_frame)

        # --- Основная панель ---
        main_split = QHBoxLayout()
        main_split.setSpacing(12)

        # Левая панель с карточками
        left_frame = QFrame()
        left_frame.setObjectName("left_frame")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("scroll_area")

        self.card_container = QWidget()
        self.card_container.setObjectName("card_container")
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setSpacing(6)
        self.card_layout.setContentsMargins(4, 4, 4, 4)
        self.card_layout.addStretch()

        scroll.setWidget(self.card_container)
        left_layout.addWidget(scroll)
        main_split.addWidget(left_frame, stretch=1)

        # Правая панель с деталями
        right_frame = QFrame()
        right_frame.setObjectName("right_frame")
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(10, 10, 10, 10)

        detail_title = QLabel("🔍 Детали сессии")
        detail_title.setObjectName("detail_title")
        right_layout.addWidget(detail_title)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setObjectName("detail_text")
        right_layout.addWidget(self.detail_text)

        self.delete_btn = QPushButton("🗑 Удалить выбранную сессию")
        self.delete_btn.clicked.connect(self._delete_selected_session)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setObjectName("delete_btn")
        right_layout.addWidget(self.delete_btn)

        main_split.addWidget(right_frame, stretch=1)
        layout.addLayout(main_split)

    def _create_quick_btn(self, text: str, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setObjectName("quick_btn")
        return btn

    # ---------- Фильтры ----------
    def _set_quick_date(self, days_back: int):
        today = datetime.now().date()
        if days_back == 0:
            from_date = today
            to_date = today
        else:
            from_date = today - timedelta(days=days_back)
            to_date = today
        self.filter_from.setText(from_date.strftime("%Y-%m-%d"))
        self.filter_to.setText(to_date.strftime("%Y-%m-%d"))
        self._apply_filter()

    def _set_all_time(self):
        self.filter_from.setText("")
        self.filter_to.setText("")
        self._apply_filter()

    def _apply_filter(self):
        raw = self._get_sessions()
        self.filtered_sessions = self._sort_sessions(raw)

        self._update_aggregated_stats()
        self._build_cards()

        if self.selected_session in self.filtered_sessions:
            self._show_details(self.selected_session)
        else:
            self.selected_session = None
            self.detail_text.clear()
            self.delete_btn.setEnabled(False)

    def _get_sessions(self) -> List[Session]:
        sessions = self.logic.sessions.copy()
        if self.logic.session_active and self.logic.session_start:
            now = time.time()
            live = Session(
                started_at=self.logic.session_start,
                ended_at=now,
                points=self.logic.session_points,
                tab_times=dict(self.logic.tab_times),
            )
            sessions.append(live)

        date_from = self.filter_from.text().strip()
        date_to = self.filter_to.text().strip()
        if date_from:
            try:
                from_ts = time.mktime(time.strptime(date_from, "%Y-%m-%d"))
                sessions = [s for s in sessions if s.started_at >= from_ts]
            except ValueError:
                pass
        if date_to:
            try:
                to_ts = time.mktime(time.strptime(date_to, "%Y-%m-%d")) + 24*3600 - 1
                sessions = [s for s in sessions if s.started_at <= to_ts]
            except ValueError:
                pass
        return sessions

    def _sort_sessions(self, sessions: List[Session]) -> List[Session]:
        sort_key = self.sort_combo.currentText()
        if sort_key == "📅 по дате (новые)":
            return sorted(sessions, key=lambda s: s.started_at, reverse=True)
        elif sort_key == "📅 по дате (старые)":
            return sorted(sessions, key=lambda s: s.started_at)
        elif sort_key == "📈 по точкам (↑)":
            return sorted(sessions, key=lambda s: s.points)
        elif sort_key == "📈 по точкам (↓)":
            return sorted(sessions, key=lambda s: s.points, reverse=True)
        elif sort_key == "⚡ по скорости (↑)":
            return sorted(sessions, key=lambda s: s.points / (get_productive_tab_time(s.tab_times) / 3600) if get_productive_tab_time(s.tab_times) > 0 else 0)
        elif sort_key == "⚡ по скорости (↓)":
            return sorted(sessions, key=lambda s: s.points / (get_productive_tab_time(s.tab_times) / 3600) if get_productive_tab_time(s.tab_times) > 0 else 0, reverse=True)
        return sessions

    # ---------- Статистика ----------
    def _update_aggregated_stats(self):
        sessions = self.filtered_sessions
        if not sessions:
            self.stats_label.setText("📭 Нет данных за выбранный период")
            return

        count = len(sessions)
        total_points = sum(s.points for s in sessions)
        total_productive = sum(get_productive_tab_time(s.tab_times) for s in sessions)
        total_duration = sum(s.duration for s in sessions)
        total_earnings = total_points * self.logic.point_price

        avg_speed = calc_points_per_hour(total_points, total_productive)
        avg_speed_str = f"{avg_speed:.1f} точ/ч" if avg_speed is not None else "—"
        avg_per_session = total_points / count if count else 0

        date_from = self.filter_from.text().strip()
        date_to = self.filter_to.text().strip()
        if date_from and date_to:
            if date_from == date_to:
                period_label = f"📅 {date_from}"
            else:
                period_label = f"📅 {date_from} → {date_to}"
        else:
            period_label = "📅 Всё время"

        text = (
            f"{period_label}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Сессий: {count}  |  📊 Всего точек: {total_points}  |  📈 Среднее: {avg_per_session:.1f}\n"
            f"⏱ Время в панорамах: {format_duration(total_productive)}  |  🕐 Общая длительность: {format_duration(total_duration)}\n"
            f"⚡ Средняя скорость: {avg_speed_str}  |  💰 Заработано: {total_earnings:.2f} руб."
        )
        self.stats_label.setText(text)

    # ---------- Карточки ----------
    def _build_cards(self):
        for card in self.card_frames:
            self.card_layout.removeWidget(card)
            card.deleteLater()
        self.card_frames.clear()

        for session in self.filtered_sessions:
            card = self._create_card(session)
            self.card_frames.append(card)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)

    def _create_card(self, session: Session) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setCursor(Qt.PointingHandCursor)

        start = time.localtime(session.started_at)
        end = time.localtime(session.ended_at)
        prod_secs = get_productive_tab_time(session.tab_times)
        pph = format_points_per_hour(session.points, prod_secs)
        earnings = session.points * self.logic.point_price
        duration = session.duration

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        top_layout = QHBoxLayout()
        date_label = QLabel(
            f"{start.tm_mday:02d}.{start.tm_mon:02d}.{start.tm_year} "
            f"{start.tm_hour:02d}:{start.tm_min:02d} → {end.tm_hour:02d}:{end.tm_min:02d}"
        )
        date_label.setObjectName("card_date")
        top_layout.addWidget(date_label)
        top_layout.addStretch()

        points_label = QLabel(f"⚡ {session.points}")
        points_label.setObjectName("card_points")
        top_layout.addWidget(points_label)
        layout.addLayout(top_layout)

        bottom_label = QLabel(
            f"⚡ {pph}  |  ⏱ {format_duration(duration)}  |  💰 {earnings:.2f} руб."
        )
        bottom_label.setObjectName("card_stats")
        layout.addWidget(bottom_label)

        card.session = session

        def on_click(e, s=session):
            self._on_card_click(s)
        card.mousePressEvent = on_click

        return card

    def _on_card_click(self, session: Session):
        self.selected_session = session
        self._show_details(session)

        for card in self.card_frames:
            if hasattr(card, 'session') and card.session == session:
                card.setStyleSheet("""
                    QFrame#card {
                        background-color: #1a2a4a;
                        border: 2px solid #00d4aa;
                        border-radius: 6px;
                        padding: 8px;
                    }
                """)
            else:
                card.setStyleSheet("""
                    QFrame#card {
                        background-color: #1a1a3e;
                        border: 1px solid #2a2a5e;
                        border-radius: 6px;
                        padding: 8px;
                    }
                    QFrame#card:hover {
                        background-color: #22225a;
                        border-color: #3d3d7b;
                    }
                """)

    # ---------- Детали ----------
    def _show_details(self, session: Session):
        self.detail_text.clear()
        prod_secs = get_productive_tab_time(session.tab_times)
        pph = format_points_per_hour(session.points, prod_secs)
        earnings = session.points * self.logic.point_price

        lines = [
            f"📌 Начало:  {format_datetime(session.started_at)}",
            f"🏁 Конец:   {format_datetime(session.ended_at)}",
            f"⏱ Длительность: {format_duration(session.duration)}",
            f"⏳ Чистое время в панорамах: {format_duration(prod_secs)}",
            f"📊 Точек: {session.points}",
            f"⚡ Скорость: {pph}",
            f"💰 Заработано: {earnings:.2f} руб.",
            "",
            "📋 Время по вкладкам:"
        ]
        self.detail_text.setText("\n".join(lines))
        if session.tab_times:
            for title, secs in sorted(session.tab_times.items(), key=lambda x: x[1], reverse=True):
                marker = " ★" if is_productive_tab(title) else ""
                self.detail_text.append(f"  {format_duration(secs)}  →  {title}{marker}")
        else:
            self.detail_text.append("  Нет данных по вкладкам")

        self.delete_btn.setEnabled(True)

    # ---------- Удаление ----------
    def _delete_selected_session(self):
        if self.selected_session is None:
            return

        if (self.logic.session_active and self.logic.session_start and
            self.selected_session.started_at == self.logic.session_start):
            QMessageBox.information(self, "Удаление", "Нельзя удалить текущую активную сессию.")
            return

        try:
            real_idx = self.logic.sessions.index(self.selected_session)
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Сессия не найдена.")
            return

        reply = QMessageBox.question(
            self,
            "Удалить сессию",
            f"Вы уверены, что хотите удалить сессию от {format_datetime(self.selected_session.started_at)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        removed = self.logic.sessions.pop(real_idx)
        self.logic.points = max(0, self.logic.points - removed.points)
        self.logic.level = calc_level(self.logic.points)

        from storage import save_progress
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
        )

        self.selected_session = None
        self.logic.on_update()
        self._apply_filter()