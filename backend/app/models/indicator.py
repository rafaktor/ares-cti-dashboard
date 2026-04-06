from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Indicator:
    ioc: str
    type: str            # ip | domain | hash
    score: int           # 0-100 aggregated risk score
    sources: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    country: Optional[str] = None
    last_seen: Optional[str] = None
    raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
