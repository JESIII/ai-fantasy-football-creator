from dataclasses import dataclass
from typing import Optional

@dataclass
class Player:
    id: str
    name: str
    position: str  # QB, RB, WR, TE, DST
    team: str
    opponent: Optional[str]
    proj: float
    salary: int
    is_dst: bool = False
