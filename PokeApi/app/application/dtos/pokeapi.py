from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PokeApiPostDTO:
    name: str
    url: str

@dataclass
class PokeApiPostListDTO:
    count: int
    results: List[PokeApiPostDTO]