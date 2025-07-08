from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import uuid

@dataclass
class Comment:
    id: str
    post_id: int
    flavor: str
    potency: int
    raw_data: Dict
    created_at: str = datetime.utcnow().isoformat()

    @classmethod
    def create(cls, post_id: int, flavor_data: Dict) -> 'Comment':
        return cls(
            id=str(uuid.uuid4()),
            post_id=post_id,
            flavor=flavor_data['flavor']['name'],
            potency=flavor_data['potency'],
            raw_data=flavor_data
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "flavor": self.flavor,
            "potency": self.potency,
            "raw_data": self.raw_data,
            "created_at": self.created_at
        }