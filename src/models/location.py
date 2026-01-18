from dataclasses import dataclass
import math

@dataclass
class Location:
    id: int
    x: float
    y: float
    name: str
    demand: int = 1
    priority: int = 1  # 1=Normal, 2=High, 3=Critical
    type: str = "delivery" # 'depot', 'delivery', 'gas_station'

    def distance_to(self, other: 'Location') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
