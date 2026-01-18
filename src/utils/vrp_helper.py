from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle

class VRPHelper:
    @staticmethod
    def split_route_fleet(tour: List[Location], fleet: List[Vehicle]) -> Tuple[List[List[Location]], List[Location]]:
        """
        Splits tour into routes for specific vehicles in the fleet.
        Returns (assigned_routes, unassigned_locations).
        """
        routes = []
        tour_idx = 0
        
        for vehicle in fleet:
            current_route = []
            current_load = 0
            
            while tour_idx < len(tour):
                loc = tour[tour_idx]
                if current_load + loc.demand <= vehicle.capacity:
                    current_route.append(loc)
                    current_load += loc.demand
                    tour_idx += 1
                else:
                    break
            
            routes.append(current_route)
        
        return routes, tour[tour_idx:]

    @staticmethod
    def process_route_refueling(route: List[Location], vehicle: Vehicle, depot: Location, gas_stations: List[Location]) -> Tuple[List[Location], float, bool]:
        """
        Inserts gas stations if necessary.
        Returns (new_route, total_distance, is_feasible).
        """
        if not route:
            return [], 0.0, True

        final_route = []
        current_loc = depot
        current_fuel = vehicle.max_distance
        total_dist = 0.0
        feasible = True
        
        # Path including return to depot. We iterate stops.
        # We assume 'route' only contains deliveries initially.
        path_to_visit = route + [depot]
        
        for next_loc in path_to_visit:
            dist = current_loc.distance_to(next_loc)
            
            if dist <= current_fuel:
                # Can reach next
                if next_loc != depot: 
                     final_route.append(next_loc)
                total_dist += dist
                current_fuel -= dist
                current_loc = next_loc
            else:
                # Need fuel. Find reachable gas station.
                reachable_stations = [g for g in gas_stations if current_loc.distance_to(g) <= current_fuel]
                
                if not reachable_stations:
                    feasible = False # Stranded
                    # Add anyway to complete path for penalty calc
                    if next_loc != depot: final_route.append(next_loc)
                    total_dist += dist 
                    current_loc = next_loc
                    current_fuel = 0 # Empty
                else:
                    # Pick station closest to next_loc to minimize detour
                    best_station = min(reachable_stations, key=lambda g: g.distance_to(next_loc))
                    
                    # Go to station
                    dist_to_station = current_loc.distance_to(best_station)
                    final_route.append(best_station)
                    total_dist += dist_to_station
                    
                    # Refuel
                    current_fuel = vehicle.max_distance
                    current_loc = best_station
                    
                    # Now go to next_loc
                    dist_station_to_next = best_station.distance_to(next_loc)
                    if dist_station_to_next > current_fuel:
                        feasible = False # Even full tank can't reach
                    
                    if next_loc != depot: final_route.append(next_loc)
                    total_dist += dist_station_to_next
                    current_fuel -= dist_station_to_next
                    current_loc = next_loc

        return final_route, total_dist, feasible

    @staticmethod
    def calculate_priority_score(routes: List[List[Location]]) -> float:
        """
        Calculates a score based on priority. 
        """
        score = 0.0
        for route in routes:
            for i, loc in enumerate(route):
                # Gas stations (type='gas_station') usually shouldn't incur priority penalty, 
                # or their priority is low (1).
                # But delaying a Critical delivery (prio 3) because of a gas station (prio 1) 
                # will naturally increase the index of the critical delivery.
                score += (i + 1) * (loc.priority ** 2)
        return score