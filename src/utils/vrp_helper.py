import functools
from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle

class VRPHelper:
    @staticmethod
    @functools.lru_cache(maxsize=10000)
    def _split_route_fleet_memoized(tour_ids: Tuple[int, ...], 
                                    depot_id: int, 
                                    fleet_data: Tuple[Tuple[int, int, float], ...], 
                                    gas_station_ids: Tuple[int, ...],
                                    # We don't pass objects here to keep the key simple and hashable
                                    ) -> Tuple[List[List[int]], float, int]:
        """
        Internal memoized version of split_route_fleet. 
        Returns IDs of locations instead of objects to keep it simple.
        """
        # Note: This version needs access to the objects to do the math.
        # But wait, if I don't have the objects, I can't do distance_to.
        # This approach is flawed if I don't have a global lookup.
        pass

    @staticmethod
    def split_route_fleet(tour: List[Location], depot: Location, fleet: List[Vehicle], gas_stations: List[Location]) -> Tuple[List[List[Location]], float, int]:
        """
        Splits tour into routes, handling Capacity AND Fuel constraints dynamically.
        Inserts gas stations and depot returns as needed.
        Returns: (routes, total_distance, unassigned_count)
        """
        # Create hashable keys for memoization
        tour_ids = tuple(loc.id for loc in tour)
        fleet_data = tuple((v.id, v.capacity, v.max_distance) for v in fleet)
        gas_station_ids = tuple(s.id for s in gas_stations)
        depot_id = depot.id
        
        key = (tour_ids, depot_id, fleet_data, gas_station_ids)
        
        if not hasattr(VRPHelper, "_vrp_cache"):
            VRPHelper._vrp_cache = {}
        
        if key in VRPHelper._vrp_cache:
            return VRPHelper._vrp_cache[key]

        # Actual Logic (moved back here)
        routes = []
        total_distance = 0.0
        total_assigned = 0
        
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
                            break 
                    continue

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
                        break

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
                        total_distance += 10000.0
            
            routes.append(route)

        unassigned_count = len(tour) - total_assigned
        result = (routes, total_distance, unassigned_count)
        
        # Limit cache size to prevent memory leak
        if len(VRPHelper._vrp_cache) > 10000:
            VRPHelper._vrp_cache.clear()
            
        VRPHelper._vrp_cache[key] = result
        return result

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
        """
        The bigger the score, the worse a route is.
        The algorithm tries to recompensate the routes that passes through the higher priotity points first
        """
        score = 0.0
        for route in routes:
            for i, loc in enumerate(route):
                if getattr(loc, 'type', 'delivery') == 'delivery':
                    score += (i + 1) * (loc.priority ** 2)
        return score