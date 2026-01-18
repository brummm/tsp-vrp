from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle

class VRPHelper:
    @staticmethod
    def split_route_fleet(tour: List[Location], depot: Location, fleet: List[Vehicle], gas_stations: List[Location]) -> Tuple[List[List[Location]], float, int]:
        """
        Splits tour into routes, handling Capacity AND Fuel constraints dynamically.
        Inserts gas stations and depot returns as needed.
        Returns: (routes, total_distance, unassigned_count)
        """
        routes = []
        total_distance = 0.0
        total_assigned = 0
        
        # Chunking strategy
        num_vehicles = len(fleet)
        if num_vehicles == 0:
            return [], 0.0, len(tour)

        avg_len = len(tour) // num_vehicles
        remainder = len(tour) % num_vehicles
        start_idx = 0
        
        for i, vehicle in enumerate(fleet):
            chunk_size = avg_len + (1 if i < remainder else 0)
            chunk = tour[start_idx : start_idx + chunk_size]
            start_idx += chunk_size
            
            route = []
            current_loc = depot
            current_fuel = vehicle.max_distance
            current_load = 0
            
            

            chunk_idx = 0
            while chunk_idx < len(chunk):
                target = chunk[chunk_idx]
                
                # 1. Capacity Check
                if current_load + target.demand > vehicle.capacity:
                    dist_to_depot = current_loc.distance_to(depot)
                    if dist_to_depot <= current_fuel:
                        route.append(depot)
                        total_distance += dist_to_depot
                        current_loc = depot
                        current_fuel = vehicle.max_distance
                        current_load = 0
                    else:
                        station, dist = VRPHelper.find_refuel_path(vehicle, current_loc, depot, current_fuel, gas_stations)
                        if station:
                            route.append(station)
                            route.append(depot)
                            total_distance += dist
                            current_loc = depot
                            current_fuel = vehicle.max_distance
                            current_load = 0
                        else:
                            # Stranded (cannot reach depot to reload)
                            break 
                    continue

                # 2. Fuel Check to Target
                dist_to_target = current_loc.distance_to(target)
                if dist_to_target <= current_fuel:
                    route.append(target)
                    total_distance += dist_to_target
                    current_loc = target
                    current_fuel -= dist_to_target
                    current_load += target.demand
                    total_assigned += 1
                    chunk_idx += 1
                else:
                    station, dist = VRPHelper.find_refuel_path(vehicle, current_loc, target, current_fuel, gas_stations)
                    if station:
                        route.append(station)
                        route.append(target)
                        total_distance += dist
                        current_loc = target
                        current_fuel = vehicle.max_distance - station.distance_to(target)
                        current_load += target.demand
                        total_assigned += 1
                        chunk_idx += 1
                    else:
                        # Stranded (cannot reach target)
                        break

            # Return to Depot
            if route and route[-1] != depot:
                dist_to_depot = current_loc.distance_to(depot)
                if dist_to_depot <= current_fuel:
                    route.append(depot)
                    total_distance += dist_to_depot
                else:
                    station, dist = VRPHelper.find_refuel_path(vehicle, current_loc, depot, current_fuel, gas_stations)
                    if station:
                        route.append(station)
                        route.append(depot)
                        total_distance += dist
                    else:
                        # Stranded on return. 
                        total_distance += 10000.0 # Penalty for not returning safe
            
            routes.append(route)

        unassigned_count = len(tour) - total_assigned
        return routes, total_distance, unassigned_count

    @staticmethod
    def find_refuel_path(vehicle: Vehicle, from_loc: Location, to_loc: Location, current_fuel: float, gas_stations: List[Location]):
        candidates = [s for s in gas_stations if from_loc.distance_to(s) <= current_fuel]
        if not candidates: return None, float('inf')
        valid = [s for s in candidates if s.distance_to(to_loc) <= vehicle.max_distance]
        if not valid: return None, float('inf')
        best = min(valid, key=lambda s: from_loc.distance_to(s) + s.distance_to(to_loc))
        dist = from_loc.distance_to(best) + best.distance_to(to_loc)
        return best, dist
    
    @staticmethod
    def calculate_priority_score(routes: List[List[Location]]) -> float:
        score = 0.0
        for route in routes:
            for i, loc in enumerate(route):
                if getattr(loc, 'type', 'delivery') == 'delivery':
                    score += (i + 1) * (loc.priority ** 2)
        return score