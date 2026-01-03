from dataclasses import dataclass

@dataclass
class Vehicle:
    id: int
    capacity: int
    speed_kmh: float = 60.0
    max_distance: float = float('inf')
