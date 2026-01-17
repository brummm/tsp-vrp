import json
from typing import List
from src.models.location import Location

class DataLoader:
    @staticmethod
    def load_locations(file_path: str) -> List[Location]:
        """
        Loads locations from a JSON file.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        locations = []
        for item in data:
            locations.append(Location(
                id=item['id'],
                x=item['x'],
                y=item['y'],
                name=item['name'],
                demand=item.get('demand', 1),
                priority=item.get('priority', 1)
            ))
        return locations
