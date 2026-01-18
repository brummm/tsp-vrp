import json
import os
from typing import List
from src.models.location import Location

class DataLoader:
    @staticmethod
    def load_data(limit: int, data_dir: str = 'data') -> List[Location]:
        """
        Loads 'limit' delivery locations from locations_large.json 
        and ALL gas stations from gas_stations.json.
        """
        # Determine paths
        loc_path = os.path.join(data_dir, 'locations_large.json')
        gas_path = os.path.join(data_dir, 'gas_stations.json')
        
        locations = []
        
        # Load Deliveries
        if os.path.exists(loc_path):
            with open(loc_path, 'r') as f:
                data = json.load(f)
                # Slice top to bottom
                data = data[:limit]
                for item in data:
                    locations.append(Location(
                        id=item['id'],
                        x=item['x'],
                        y=item['y'],
                        name=item['name'],
                        demand=item.get('demand', 1),
                        priority=item.get('priority', 1),
                        type=item.get('type', 'delivery')
                    ))
        else:
            raise FileNotFoundError(f"Could not find {loc_path}")

        # Load Gas Stations
        if os.path.exists(gas_path):
            with open(gas_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    locations.append(Location(
                        id=item['id'],
                        x=item['x'],
                        y=item['y'],
                        name=item['name'],
                        demand=item.get('demand', 0),
                        priority=item.get('priority', 1),
                        type=item.get('type', 'gas_station')
                    ))
        else:
             raise FileNotFoundError(f"Could not find {gas_path}")
             
        return locations
