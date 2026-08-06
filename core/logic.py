"""
Основная бизнес-логика приложения.
"""
import time
import math
from typing import Optional, List, Dict, Callable, Any

import keyboard

from core.config import RANKS
from core.models import Session
from core.utils import (
    calc_level, get_productive_tab_time,
    parse_tab_title, get_active_window_title,
    calc_points_per_hour, is_productive_tab
)
from core.notifications import send_notification


class TrackerLogic:
    def __init__(self, on_update=None, on_beep=None, on_level_up=None):
        self.on_update = on_update or (lambda: None)
        self.on_beep = on_beep or (lambda f, d: None)
        self.on_level_up = on_level_up or (lambda: None)

        # Общее количество точек
        self.points = 0
        self.level = 1

        # Настройки (будут загружены из settings.json)
        self.sprint_duration = 15
        self.break_duration = 5
        self.sprint_repeats = 1
        self.point_price = 1.3
        self.auto_save_interval = 60
        self.sound_enabled = True
        self.auto_goal_adjustment = True

        # Цель на день
        self.daily_goal = 0
        self.goal_start_date = time.strftime("%Y-%m-%d")
        self._goal_achieved_notified = False

        # Сессии и состояние
        self.session_active = False
        self.session_start: Optional[float] = None
        self.session_points = 0
        self.tab_times: Dict[str, float] = {}
        self.current_tab = ""
        self._last_tab_poll = 0.0
        self.sessions: List[Session] = []

        # Фазы спринта
        self.current_phase = "idle"
        self.current_phase_start: Optional[float] = None
        self.current_sprint_index = 0
        self.sprint_finished = False
        self._recording = False

        # Флаги для предупреждений
        self._sprint_warning_sent = False
        self._break_warning_sent = False

        # Хоткей
        self._hotkey_registered = False
        self._hotkey_latch = False
        self._hotkey_handle = None
        self._closing = False

        # Автосохранение
        self.last_auto_save = time.time()

        # Рекорды
        self.records: Dict[str, Any] = {
            "max_points_per_day": 0,
            "max_points_per_sprint": 0,
            "max_speed_per_session": 0.0,
            "max_speed_per_day": 0.0,
        }

    # ---------- Ранги ----------
    def get_rank(self) -> str:
        rank = "Стажёр"
        for threshold, name in sorted(RANKS.items()):
            if self.points >= threshold:
                rank = name
        return rank

    # ---------- Точки за сегодня ----------
    def get_today_points(self) -> int:
        today = time.strftime("%Y-%m-%d")
        total = 0
        for sess in self.sessions:
            if time.strftime("%Y-%m-%d", time.localtime(sess.started_at)) == today:
                total += sess.points
        if self.session_active and self.session_start:
            if time.strftime("%Y-%m-%d", time.localtime(self.session_start)) == today:
                total += self.session_points
        return total

    # ---------- Заработок ----------
    def get_today_earnings(self) -> float:
        return self.get_today_points() * self.point_price

    def get_total_earnings(self) -> float:
        return self.points * self.point_price

    def get_session_earnings(self, session: Session) -> float:
        return session.points * self.point_price

    # ---------- Цели ----------
    def set_daily_goal(self, goal_points: int) -> None:
        self.daily_goal = max(0, goal_points)
        self.goal_start_date = time.strftime("%Y-%m-%d")
        self._goal_achieved_notified = False
        self.on_update()

    def get_goal_progress(self) -> float:
        if self.daily_goal <= 0:
            return 0.0
        today_pts = self.get_today_points()
        return min(1.0, today_pts / self.daily_goal)

    def get_goal_eta(self) -> Optional[float]:
        goal = self.daily_goal
        if goal <= 0:
            return None
        today_points = self.get_today_points()
        remaining = goal - today_points
        if remaining <= 0:
            return 0.0
        current_speed = None
        if self.session_active and self.session_points > 0:
            prod_time = self.get_current_productive_seconds()
            if prod_time > 0:
                current_speed = self.session_points / (prod_time / 3600)
        if current_speed is None:
            today = time.strftime("%Y-%m-%d")
            total_pts = 0
            total_prod = 0.0
            for sess in self.sessions:
                if time.strftime("%Y-%m-%d", time.localtime(sess.started_at)) == today:
                    total_pts += sess.points
                    total_prod += get_productive_tab_time(sess.tab_times)
            if total_prod > 0:
                current_speed = total_pts / (total_prod / 3600)
        if current_speed is None or current_speed <= 0:
            return None
        return remaining / current_speed

    def suggest_goal_adjustment(self) -> Optional[int]:
        if not self.auto_goal_adjustment:
            return None
        if self.daily_goal <= 0:
            return None
        today = time.strftime("%Y-%m-%d")
        last_7_days = {}
        for sess in self.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            if day == today:
                continue
            last_7_days[day] = last_7_days.get(day, 0) + sess.points
        if len(last_7_days) < 5:
            return None
        over_perform = 0
        for day, pts in last_7_days.items():
            if pts > self.daily_goal * 1.1:
                over_perform += 1
        if over_perform >= 3:
            new_goal = int(math.ceil(self.daily_goal * 1.15 / 10) * 10)
            return new_goal
        return None

    def _check_day_change(self) -> None:
        today = time.strftime("%Y-%m-%d")
        if self.goal_start_date != today and self.daily_goal > 0:
            self.daily_goal = 0
            self.goal_start_date = today
            self._goal_achieved_notified = False
            self.on_update()

    # ---------- Рекорды ----------
    def update_records(self):
        daily = {}
        for sess in self.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            daily[day] = daily.get(day, 0) + sess.points
        if daily:
            max_day = max(daily.values())
            if max_day > self.records["max_points_per_day"]:
                self.records["max_points_per_day"] = max_day

        for sess in self.sessions:
            if sess.points > self.records["max_points_per_sprint"]:
                self.records["max_points_per_sprint"] = sess.points

        # Максимальная скорость за сессию (только если сессия длилась > 30 секунд)
        for sess in self.sessions:
            prod = get_productive_tab_time(sess.tab_times)
            if prod > 30:
                speed = sess.points / (prod / 3600)
                if speed > self.records["max_speed_per_session"]:
                    self.records["max_speed_per_session"] = speed

        daily_speed = {}
        for sess in self.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            prod = get_productive_tab_time(sess.tab_times)
            if prod > 30:
                if day not in daily_speed:
                    daily_speed[day] = {"points": 0, "time": 0}
                daily_speed[day]["points"] += sess.points
                daily_speed[day]["time"] += prod

        for day, data in daily_speed.items():
            if data["time"] > 0:
                speed = data["points"] / (data["time"] / 3600)
                if speed > self.records["max_speed_per_day"]:
                    self.records["max_speed_per_day"] = speed

    # ---------- Продуктивность по часам ----------
    def get_productivity_by_hour(self) -> Dict[int, Dict]:
        hours = {}
        for sess in self.sessions:
            start_hour = time.localtime(sess.started_at).tm_hour
            if start_hour not in hours:
                hours[start_hour] = {"points": 0, "productive_seconds": 0}
            hours[start_hour]["points"] += sess.points
            hours[start_hour]["productive_seconds"] += get_productive_tab_time(sess.tab_times)
        return hours

    # ---------- Прогноз ----------
    def get_daily_points_series(self) -> dict:
        daily = {}
        for sess in self.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            daily[day] = daily.get(day, 0) + sess.points
        if self.session_active and self.session_start:
            today = time.strftime("%Y-%m-%d")
            daily[today] = daily.get(today, 0) + self.session_points
        return daily

    def predict_future_points(self, days_ahead: int = 7) -> dict:
        daily = self.get_daily_points_series()
        if len(daily) < 2:
            return {}

        dates = sorted(daily.keys())
        values = [daily[d] for d in dates]

        first_date = time.strptime(dates[0], "%Y-%m-%d")
        first_ts = time.mktime(first_date)
        x = []
        for d in dates:
            ts = time.mktime(time.strptime(d, "%Y-%m-%d"))
            x.append((ts - first_ts) / (24 * 3600))

        n = len(x)
        if n < 2:
            return {}

        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        a = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
        b = (sum_y - a * sum_x) / n

        last_day = dates[-1]
        last_ts = time.mktime(time.strptime(last_day, "%Y-%m-%d"))
        last_day_num = (last_ts - first_ts) / (24 * 3600)

        predictions = {}
        for i in range(1, days_ahead + 1):
            future_day_num = last_day_num + i
            predicted = a * future_day_num + b
            if predicted < 0:
                predicted = 0
            future_ts = first_ts + future_day_num * 24 * 3600
            future_date = time.strftime("%Y-%m-%d", time.localtime(future_ts))
            predictions[future_date] = round(predicted, 1)

        return predictions

    # ---------- Звуки предупреждений ----------
    def _play_warning_sound(self, pattern: str = "short"):
        """Воспроизвести звук предупреждения (без потоков)."""
        if not self.sound_enabled:
            return

        try:
            import winsound
            
            if pattern == "short":
                winsound.Beep(880, 150)
                import time
                time.sleep(0.1)
                winsound.Beep(880, 150)
                
            elif pattern == "long":
                winsound.Beep(440, 300)
                import time
                time.sleep(0.15)
                winsound.Beep(660, 300)
                
            elif pattern == "sprint_end":
                winsound.Beep(880, 200)
                import time
                time.sleep(0.1)
                winsound.Beep(660, 200)
                
        except Exception:
            pass

    # ---------- Сессия ----------
    def start_session(self) -> None:
        if self.session_active:
            return
        now = time.time()
        self.session_active = True
        self.session_start = now
        self.session_points = 0
        self.tab_times = {}
        self.current_tab = ""
        self._last_tab_poll = now
        self.current_sprint_index = 0
        self.sprint_finished = False
        self._goal_achieved_notified = False
        self._sprint_warning_sent = False
        self._break_warning_sent = False

        self._start_phase("sprint")
        self.on_beep(660, 80)
        self.on_update()

    def stop_session(self) -> None:
        if not self.session_active:
            return
        self._flush_tab_time()
        now = time.time()
        started = self.session_start or now

        session = Session(
            started_at=started,
            ended_at=now,
            points=self.session_points,
            tab_times=dict(self.tab_times),
        )
        self.sessions.append(session)
        self.update_records()

        self.session_active = False
        self.session_start = None
        self.current_phase = "idle"
        self.current_phase_start = None
        self.sprint_finished = False
        self.current_sprint_index = 0
        self._recording = False
        self._sprint_warning_sent = False
        self._break_warning_sent = False

        self.on_beep(440, 100)
        self.on_update()

    # ---------- Спринты ----------
    def _start_phase(self, phase: str) -> None:
        if not self.session_active:
            return
        self.current_phase = phase
        self.current_phase_start = time.time()
        self._recording = (phase == "sprint")
        self._sprint_warning_sent = False
        self._break_warning_sent = False

        if phase == "sprint":
            self._play_warning_sound("short")
            if self.current_sprint_index + 1 <= self.sprint_repeats:
                send_notification(
                    "🚀 Спринт начался",
                    f"Спринт {self.current_sprint_index + 1}/{self.sprint_repeats}\nРаботай продуктивно!"
                )
        else:
            self._play_warning_sound("long")
            send_notification(
                "☕ Перерыв",
                f"Перерыв {self.current_sprint_index + 1}/{self.sprint_repeats}\nОтдохни!"
            )
        self.on_update()

    def _check_phase_complete(self) -> None:
        if not self.session_active or self.current_phase_start is None:
            return
        elapsed = time.time() - self.current_phase_start

        if self.current_phase == "sprint":
            duration = self.sprint_duration * 60
            remaining = duration - elapsed

            # Предупреждение за 10 секунд до конца спринта
            if remaining <= 10 and remaining > 0 and not self._sprint_warning_sent:
                self._sprint_warning_sent = True
                self._play_warning_sound("short")
                send_notification(
                    "⏰ Спринт заканчивается!",
                    f"Осталось {int(remaining)} секунд!"
                )

            if remaining > 10:
                self._sprint_warning_sent = False

            if elapsed >= duration:
                self._sprint_warning_sent = False
                if self.current_sprint_index < self.sprint_repeats - 1:
                    self.current_sprint_index += 1
                    self._start_phase("break")
                else:
                    self.sprint_finished = True
                    self.current_phase = "idle"
                    self.current_phase_start = None
                    self._recording = False
                    self._play_warning_sound("sprint_end")
                    send_notification(
                        "🎉 Все спринты завершены!",
                        f"Вы сделали {self.session_points} точек.\nОтличная работа!"
                    )
                    self.on_update()
        else:
            duration = self.break_duration * 60
            remaining = duration - elapsed

            # Предупреждение за 5 секунд до конца перерыва
            if remaining <= 5 and remaining > 0 and not self._break_warning_sent:
                self._break_warning_sent = True
                self._play_warning_sound("long")
                send_notification(
                    "⏰ Перерыв заканчивается!",
                    f"Осталось {int(remaining)} секунд!\nГотовься к работе!"
                )

            if remaining > 5:
                self._break_warning_sent = False

            if elapsed >= duration:
                self._break_warning_sent = False
                self._start_phase("sprint")

    def _update_phase_progress(self) -> tuple[Optional[str], float, float]:
        if not self.session_active or self.current_phase_start is None:
            return None, 0.0, 0.0
        elapsed = time.time() - self.current_phase_start
        if self.current_phase == "sprint":
            total = self.sprint_duration * 60
        elif self.current_phase == "break":
            total = self.break_duration * 60
        else:
            return None, 0.0, 0.0
        remaining = max(0.0, total - elapsed)
        progress = elapsed / total if total > 0 else 0
        return self.current_phase, remaining, min(progress, 1.0)

    # ---------- Нажатия ----------
    def on_point(self) -> None:
        if not self.session_active:
            self.on_beep(300, 80)
            return

        if self.current_phase == "break":
            self.on_beep(200, 100)
            return

        if self.current_phase != "sprint" or self.sprint_finished:
            self.on_beep(300, 80)
            return

        self.points += 1
        self.session_points += 1

        new_level = calc_level(self.points)
        if new_level > self.level:
            self.level = new_level
            self.on_level_up()
        else:
            self.on_beep(880, 60)

        # Проверка достижения цели
        if self.daily_goal > 0:
            progress = self.get_goal_progress()
            if progress >= 1.0 and not self._goal_achieved_notified:
                self._goal_achieved_notified = True
                send_notification(
                    "🎯 Цель достигнута!",
                    f"Вы выполнили цель на сегодня: {self.daily_goal} точек!\nМожно отдыхать."
                )

        self.on_update()

    # ---------- Вкладки ----------
    def _flush_tab_time(self) -> None:
        if not self.session_active or not self.current_tab or not self._recording:
            return
        now = time.time()
        elapsed = now - self._last_tab_poll
        if elapsed > 0:
            self.tab_times[self.current_tab] = (
                self.tab_times.get(self.current_tab, 0.0) + elapsed
            )
        self._last_tab_poll = now

    def poll_active_tab(self) -> None:
        if not self.session_active:
            return
        raw = get_active_window_title()
        tab = parse_tab_title(raw)
        now = time.time()

        if tab != self.current_tab:
            self._flush_tab_time()
            self.current_tab = tab
            self._last_tab_poll = now

        self.on_update()

    def get_current_productive_seconds(self) -> float:
        if not self.session_active:
            return 0.0
        productive = get_productive_tab_time(self.tab_times)
        if self._recording and self.current_tab and is_productive_tab(self.current_tab):
            now = time.time()
            elapsed = now - self._last_tab_poll
            if elapsed > 0:
                productive += elapsed
        return productive

    # ---------- Хоткей ----------
    def register_hotkey(self) -> None:
        def on_hotkey() -> None:
            if self._closing or self._hotkey_latch:
                return
            self._hotkey_latch = True
            self.on_point()

        def release_latch(_event) -> None:
            self._hotkey_latch = False

        try:
            self._hotkey_handle = keyboard.add_hotkey(
                "ctrl+a", on_hotkey, suppress=False, trigger_on_release=False
            )
            for key in ("a", "ctrl", "left ctrl", "right ctrl"):
                keyboard.on_release_key(key, release_latch, suppress=False)
            self._hotkey_registered = True
        except Exception as exc:
            print(f"Не удалось зарегистрировать Ctrl+A: {exc}")

    def unregister_hotkey(self) -> None:
        if self._hotkey_registered:
            try:
                keyboard.unhook_all()
            except Exception:
                pass
            self._hotkey_registered = False

    # ---------- Тик ----------
    def tick(self) -> None:
        if self._closing:
            return

        self._check_day_change()

        if self.session_active:
            self.poll_active_tab()
            if time.time() - self._last_tab_poll >= 500 / 1000:
                self._flush_tab_time()
                self._last_tab_poll = time.time()

        if self.session_active and self.current_phase != "idle":
            self._check_phase_complete()

        self.on_update()

    def close(self) -> None:
        self._closing = True
        if self.session_active:
            self.stop_session()
        self.unregister_hotkey()

    # ---------- Пересчёт рекордов ----------
    def recalculate_records(self):
        self.records = {
            "max_points_per_day": 0,
            "max_points_per_sprint": 0,
            "max_speed_per_session": 0.0,
            "max_speed_per_day": 0.0,
        }
        self.update_records()
        self.on_update()

    def auto_set_goal(self) -> None:
        """Автоматически установить цель на день на основе среднего за неделю + 10%."""
        today = time.strftime("%Y-%m-%d")

        if self.goal_start_date == today and self.daily_goal > 0:
            return

        last_7_days = {}
        for sess in self.sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            if day != today:
                last_7_days[day] = last_7_days.get(day, 0) + sess.points

        if len(last_7_days) < 3:
            new_goal = 100
        else:
            avg = sum(last_7_days.values()) / len(last_7_days)
            new_goal = int(math.ceil(avg * 1.1 / 10) * 10)
            new_goal = max(50, new_goal)

        self.set_daily_goal(new_goal)