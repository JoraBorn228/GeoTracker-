"""
Модели данных: частица, сессия, вспомогательные функции преобразования.
"""
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from core.config import PARTICLE_COLORS


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
        speed = random.uniform(1.5, 4.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.max_life = random.uniform(25, 45)
        self.life = self.max_life
        self.color = random.choice(PARTICLE_COLORS)
        self.size = random.uniform(3, 6)

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1
        return self.life > 0


@dataclass
class Session:
    started_at: float
    ended_at: float
    points: int
    tab_times: Dict[str, float] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return self.ended_at - self.started_at

    def to_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "points": self.points,
            "tab_times": self.tab_times,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(
            started_at=data["started_at"],
            ended_at=data["ended_at"],
            points=data.get("points", 0),
            tab_times=data.get("tab_times", {}),
        )


def sessions_from_list(data_list: List[dict]) -> List[Session]:
    return [Session.from_dict(item) for item in data_list]


def sessions_to_list(sessions: List[Session]) -> List[dict]:
    return [s.to_dict() for s in sessions]