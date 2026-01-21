import functools
from typing import List, Tuple, Dict, Any

class VRPHelper:
    @staticmethod
    def split_route_fleet(
        tour_ids: List[int], 
        depot_id: int, 
        fleet_specs: List[Tuple[int, float]], # (capacity, max_distance)
        gas_station_ids: List[int],
        distance_matrix: List[List[float]],
        demands: List[int]
    ) -> Tuple[List[List[int]], float, int]:
        """
        Splits tour (list of IDs) into routes using integer lookups only.
        """
        # Create hashable key for memoization
        # Must include fleet_specs to distinguish between different fleet configurations
        # fleet_specs is a list of tuples, so we convert list to tuple to be hashable
        
        key = (tuple(tour_ids), depot_id, tuple(fleet_specs)) 
        
        # We use a manual cache dictionary on the class to avoid passing massive static data to the key
        if not hasattr(VRPHelper, "_vrp_cache"):
            VRPHelper._vrp_cache = {}
            
        if key in VRPHelper._vrp_cache:
            return VRPHelper._vrp_cache[key]

        routes = []
        total_distance = 0.0
        total_assigned = 0
        
        num_vehicles = len(fleet_specs)
        if num_vehicles == 0:
            return [], 0.0, len(tour_ids)

        tour_len = len(tour_ids)
        avg_len = tour_len // num_vehicles
        remainder = tour_len % num_vehicles
        start_idx = 0
        
        for i, (capacity, max_dist) in enumerate(fleet_specs):
            chunk_size = avg_len + (1 if i < remainder else 0)
            # Slicing a tuple is fast
            chunk = tour_ids[start_idx : start_idx + chunk_size]
            start_idx += chunk_size
            
            route = []
            current_id = depot_id
            current_fuel = max_dist
            current_load = 0
            
            chunk_idx = 0
            while chunk_idx < len(chunk):
                target_id = chunk[chunk_idx]
                target_demand = demands[target_id]
                
                # 1. Capacity Check
                if current_load + target_demand > capacity:
                    # Return to Depot
                    dist_to_depot = distance_matrix[current_id][depot_id]
                    
                    if dist_to_depot <= current_fuel:
                        route.append(depot_id)
                        total_distance += dist_to_depot
                        current_id = depot_id
                        current_fuel = max_dist
                        current_load = 0
                    else:
                        station_id, dist = VRPHelper.find_refuel_path(
                            current_id, depot_id, current_fuel, max_dist, gas_station_ids, distance_matrix
                        )
                        if station_id is not None:
                            route.append(station_id)
                            route.append(depot_id)
                            total_distance += dist
                            current_id = depot_id
                            current_fuel = max_dist
                            current_load = 0
                        else:
                            # Stranded
                            break 
                    continue

                # 2. Fuel Check to Target
                dist_to_target = distance_matrix[current_id][target_id]
                
                if dist_to_target <= current_fuel:
                    route.append(target_id)
                    total_distance += dist_to_target
                    current_id = target_id
                    current_fuel -= dist_to_target
                    current_load += target_demand
                    total_assigned += 1
                    chunk_idx += 1
                else:
                    station_id, dist = VRPHelper.find_refuel_path(
                        current_id, target_id, current_fuel, max_dist, gas_station_ids, distance_matrix
                    )
                    if station_id is not None:
                        route.append(station_id)
                        route.append(target_id)
                        total_distance += dist
                        current_id = target_id
                        # Refueled at station -> target
                        current_fuel = max_dist - distance_matrix[station_id][target_id]
                        current_load += target_demand
                        total_assigned += 1
                        chunk_idx += 1
                    else:
                        # Stranded
                        break

            # Return to Depot
            if route and route[-1] != depot_id:
                dist_to_depot = distance_matrix[current_id][depot_id]
                if dist_to_depot <= current_fuel:
                    route.append(depot_id)
                    total_distance += dist_to_depot
                else:
                    station_id, dist = VRPHelper.find_refuel_path(
                        current_id, depot_id, current_fuel, max_dist, gas_station_ids, distance_matrix
                    )
                    if station_id is not None:
                        route.append(station_id)
                        route.append(depot_id)
                        total_distance += dist
                    else:
                        total_distance += 10000.0 # Penalty
            
            routes.append(route)

        unassigned_count = len(tour_ids) - total_assigned
        result = (routes, total_distance, unassigned_count)
        
        # Simple cache eviction
        if len(VRPHelper._vrp_cache) > 20000:
            VRPHelper._vrp_cache.clear()
            
        VRPHelper._vrp_cache[key] = result
        return result

    @staticmethod
    def find_refuel_path(from_id: int, to_id: int, current_fuel: float, max_dist: float, 
                         gas_station_ids: List[int], distance_matrix: List[List[float]]) -> Tuple[int, float]:
        """
        Finds best gas station ID using array lookups.
        """
        best_station = None
        min_total_dist = float('inf')
        
        # Iterate through station IDs directly
        for s_id in gas_station_ids:
            # Check reachability from current
            dist_to_station = distance_matrix[from_id][s_id]
            if dist_to_station <= current_fuel:
                # Check reachability to target (with full tank)
                dist_to_dest = distance_matrix[s_id][to_id]
                if dist_to_dest <= max_dist:
                    total_d = dist_to_station + dist_to_dest
                    if total_d < min_total_dist:
                        min_total_dist = total_d
                        best_station = s_id
                        
        if best_station is None:
            return None, float('inf')
            
        return best_station, min_total_dist
    
    @staticmethod
    def calculate_priority_score(routes: List[List[int]], priorities: List[int]) -> float:
        """
        Calculates score based on integer IDs and priority lookup array.
        """
        score = 0.0
        for route in routes:
            for i, loc_id in enumerate(route):
                # We need to skip depot/gas stations in priority calc if they have priority 0 or 1
                # Usually deliveries have priorities > 1 if critical. 
                # Assuming priority array has 0 for depot/gas stations if they shouldn't count.
                p = priorities[loc_id]
                if p > 1:
                    score += (i + 1) * (p ** 2)
        return score
