from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import uuid

@dataclass
class Post:
    id: int
    name: str
    growth_time: int
    max_harvest: int
    natural_gift_power: int
    size: int
    smoothness: int
    soil_dryness: int
    raw_data: Dict
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "growth_time": self.growth_time,
            "max_harvest": self.max_harvest,
            "natural_gift_power": self.natural_gift_power,
            "size": self.size,
            "smoothness": self.smoothness,
            "soil_dryness": self.soil_dryness,
            "raw_data": self.raw_data,
            "created_at": self.created_at
        }