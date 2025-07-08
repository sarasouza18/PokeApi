# app/application/dtos/__init__.py
"""
Data Transfer Objects for application layer

Contains:
- PokeApiPostDTO: DTO for PokeAPI post data
- PokeApiPostListDTO: DTO for PokeAPI post list
"""

from .pokeapi import PokeApiPostDTO, PokeApiPostListDTO

__all__ = ['PokeApiPostDTO', 'PokeApiPostListDTO']