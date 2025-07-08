# app/application/dtos/pokeapi.py
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PokeApiPostDTO:
    """
    Data Transfer Object for PokeAPI post data
    Provides a stable interface regardless of external API changes
    """
    name: str
    url: str
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'url': self.url
        }

@dataclass
class PokeApiPostListDTO:
    """
    Data Transfer Object for list of posts from PokeAPI
    Encapsulates the API response structure
    """
    count: int
    results: List[PokeApiPostDTO]
    
    def to_dict(self) -> Dict:
        return {
            'count': self.count,
            'results': [item.to_dict() for item in self.results]
        }

@dataclass
class PokeApiPostDetailDTO:
    """
    Data Transfer Object for detailed post information from PokeAPI
    Normalizes the API response for internal use
    """
    id: int
    name: str
    growth_time: int
    max_harvest: int
    natural_gift_power: int
    size: int
    smoothness: int
    soil_dryness: int
    flavors: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'growth_time': self.growth_time,
            'max_harvest': self.max_harvest,
            'natural_gift_power': self.natural_gift_power,
            'size': self.size,
            'smoothness': self.smoothness,
            'soil_dryness': self.soil_dryness,
            'flavors': self.flavors
        }