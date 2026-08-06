"""
Умная аналитика продуктивности.
"""
import time
from typing import List, Dict, Optional
from core.models import Session
from core.utils import get_productive_tab_time


class Analytics:
    @staticmethod
    def analyze_peak_hours(sessions: List[Session]) -> Dict[int, int]:
        """Определить самые продуктивные часы."""
        hours = {}
        for sess in sessions:
            hour = time.localtime(sess.started_at).tm_hour
            hours[hour] = hours.get(hour, 0) + sess.points
        return hours

    @staticmethod
    def get_best_hours(sessions: List[Session], top_n: int = 3) -> List[int]:
        """Вернуть top_n самых продуктивных часов."""
        hours = Analytics.analyze_peak_hours(sessions)
        sorted_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)
        return [h for h, _ in sorted_hours[:top_n]]

    @staticmethod
    def get_average_speed_per_day(sessions: List[Session]) -> float:
        """Средняя скорость за день (точек/час)."""
        total_points = sum(s.points for s in sessions)
        total_productive = sum(get_productive_tab_time(s.tab_times) for s in sessions)
        if total_productive <= 0:
            return 0.0
        return total_points / (total_productive / 3600)

    @staticmethod
    def get_consistency_score(sessions: List[Session]) -> float:
        """
        Оценка стабильности работы (0-100).
        Чем меньше разброс между днями, тем выше стабильность.
        """
        if len(sessions) < 3:
            return 0.0
        
        daily = {}
        for sess in sessions:
            day = time.strftime("%Y-%m-%d", time.localtime(sess.started_at))
            daily[day] = daily.get(day, 0) + sess.points
        
        values = list(daily.values())
        if len(values) < 2:
            return 0.0
        
        avg = sum(values) / len(values)
        if avg == 0:
            return 0.0
        
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        
        # Чем меньше std_dev, тем выше стабильность
        # Нормализуем: при std_dev = 0 → 100%, при std_dev = avg → 0%
        score = max(0, 100 - (std_dev / avg) * 100)
        return min(100, score)

    @staticmethod
    def get_recommendations(logic) -> List[str]:
        """Сгенерировать персонализированные рекомендации."""
        sessions = logic.sessions
        if not sessions:
            return ["Начни работать, чтобы получать рекомендации! 🚀"]

        recommendations = []
        
        # 1. Лучшее время для работы
        best_hours = Analytics.get_best_hours(sessions, top_n=2)
        if best_hours:
            hours_str = ", ".join(f"{h}:00" for h in best_hours)
            recommendations.append(f"🌟 Твои лучшие часы: {hours_str}. Работай в это время для максимума эффективности!")

        # 2. Средняя скорость
        avg_speed = Analytics.get_average_speed_per_day(sessions)
        if avg_speed > 0:
            recommendations.append(f"⚡ Средняя скорость: {avg_speed:.1f} точек/час. Попробуй поддерживать этот темп!")

        # 3. Стабильность
        consistency = Analytics.get_consistency_score(sessions)
        if consistency > 70:
            recommendations.append(f"📊 Твоя стабильность: {consistency:.0f}%. Отличная последовательность!")
        elif consistency > 40:
            recommendations.append(f"📊 Стабильность: {consistency:.0f}%. Попробуй работать в одно и то же время каждый день.")
        elif consistency > 0:
            recommendations.append(f"📊 Стабильность: {consistency:.0f}%. Постарайся выработать постоянный ритм.")

        # 4. Достижения
        total_points = logic.points
        if total_points >= 10000:
            recommendations.append("🏆 Ты Легенда! 10 000+ точек — невероятный результат!")
        elif total_points >= 5000:
            recommendations.append("🏅 Гуру картографии! 5 000+ точек — ты на высоте!")
        elif total_points >= 1000:
            recommendations.append("⭐ Ты Мастер! 1 000+ точек — отличный прогресс!")

        # 5. Если цель не достигается
        if logic.daily_goal > 0:
            today_points = logic.get_today_points()
            if today_points < logic.daily_goal * 0.5 and logic.session_active:
                recommendations.append("🎯 Ты на полпути к цели. Ускорься, осталось не так много!")
            elif today_points >= logic.daily_goal:
                recommendations.append("🎉 Ты выполнил цель на сегодня! Отличная работа!")

        # 6. Если рекомендаций нет, добавляем ободряющее сообщение
        if not recommendations:
            recommendations.append("🌟 Ты отлично работаешь! Продолжай в том же духе!")

        return recommendations