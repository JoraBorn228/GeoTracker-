"""
Загрузка и сохранение данных в JSON.
"""
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.models import Session, sessions_from_list, sessions_to_list
from core.config import SAVE_FILE, DATA_DIR


def save_progress(
    points: int,
    level: int,
    sprint_duration: int,
    break_duration: int,
    sprint_repeats: int,
    sessions: List[Session],
    session_active: bool,
    session_start: Optional[float],
    session_points: int,
    tab_times: Dict[str, float],
    daily_goal: int,
    goal_start_date: str,
    records: Dict[str, Any],
    current_phase: str = "idle",
    current_sprint_index: int = 0,
    sprint_finished: bool = False,
    current_phase_start: Optional[float] = None,
    current_tab: str = "",
    last_tab_poll: float = 0.0,
    recording: bool = False,
) -> None:
    """Сохранить прогресс, включая состояние активной сессии."""
    # Убедимся, что папка существует
    DATA_DIR.mkdir(exist_ok=True)
    
    all_sessions = sessions.copy()
    
    active_session_data = None
    if session_active:
        active_session_data = {
            "active": True,
            "started_at": session_start,
            "points": session_points,
            "tab_times": tab_times,
            "current_phase": current_phase,
            "current_sprint_index": current_sprint_index,
            "sprint_finished": sprint_finished,
            "phase_start": current_phase_start,
            "current_tab": current_tab,
            "last_tab_poll": last_tab_poll,
            "recording": recording,
        }

    data = {
        "points": points,
        "level": level,
        "sprint_duration": sprint_duration,
        "break_duration": break_duration,
        "sprint_repeats": sprint_repeats,
        "sessions": sessions_to_list(all_sessions),
        "daily_goal": daily_goal,
        "goal_start_date": goal_start_date,
        "records": records,
        "active_session": active_session_data,
    }
    
    SAVE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_progress() -> Dict[str, Any]:
    """Загрузить прогресс."""
    if not SAVE_FILE.exists():
        return {}

    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    # Миграция старых данных
    if "sessions" not in data:
        old_last = data.get("last_session")
        if old_last:
            started = old_last.get("started_at")
            ended = old_last.get("ended_at", time.time())
            if started is None:
                started = ended - old_last.get("duration", 0)
            data["sessions"] = [{
                "started_at": started,
                "ended_at": ended,
                "points": old_last.get("points", 0),
                "tab_times": old_last.get("tab_times", {}),
            }]
        else:
            data["sessions"] = []

    if "daily_goal" not in data:
        data["daily_goal"] = 0
    if "goal_start_date" not in data:
        data["goal_start_date"] = time.strftime("%Y-%m-%d")
    if "records" not in data:
        data["records"] = {
            "max_points_per_day": 0,
            "max_points_per_sprint": 0,
            "max_speed_per_session": 0.0,
            "max_speed_per_day": 0.0,
        }
    if "active_session" not in data:
        data["active_session"] = None

    return {
        "points": int(data.get("points", 0)),
        "level": int(data.get("level", 1)),
        "sprint_duration": int(data.get("sprint_duration", 15)),
        "break_duration": int(data.get("break_duration", 5)),
        "sprint_repeats": int(data.get("sprint_repeats", 1)),
        "sessions": sessions_from_list(data.get("sessions", [])),
        "daily_goal": int(data.get("daily_goal", 0)),
        "goal_start_date": data.get("goal_start_date", time.strftime("%Y-%m-%d")),
        "records": data.get("records", {}),
        "active_session": data.get("active_session"),
    }