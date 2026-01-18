from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle

class VRPHelper:
    @staticmethod
    def split_route_fleet(tour: List[Location], depot: Location, fleet: List[Vehicle]) -> Tuple[List[List[Location]], List[Location]]:
        """
        Splits tour into routes for fleet using chunking + return-to-depot for refills.
        Ensures all stops are assigned.
        """
        routes = []
        num_vehicles = len(fleet)
        if num_vehicles == 0:
            return [], tour

        # Distribute tour roughly equally among vehicles
        avg_len = len(tour) // num_vehicles
        remainder = len(tour) % num_vehicles
        
        start_idx = 0
        for i, vehicle in enumerate(fleet):
            chunk_size = avg_len + (1 if i < remainder else 0)
            chunk = tour[start_idx : start_idx + chunk_size]
            start_idx += chunk_size
            
            vehicle_route = []
            current_load = 0
            
            for loc in chunk:
                if current_load + loc.demand > vehicle.capacity:
                    # Capacity full: Return to depot to reload
                    vehicle_route.append(depot)
                    current_load = 0
                
                vehicle_route.append(loc)
                current_load += loc.demand
            
            routes.append(vehicle_route)
        
        return routes, [] # No unassigned in this strategy

    @staticmethod
    def process_route_refueling(route: List[Location], vehicle: Vehicle, depot: Location, gas_stations: List[Location]) -> Tuple[List[Location], float, bool]:
        """
        Inserts gas stations if necessary. Handles explicit Depot stops (refills).
        """
        if not route:
            return [], 0.0, True

        final_route = []
        current_loc = depot
        current_fuel = vehicle.max_distance
        total_dist = 0.0
        feasible = True
        
        # We need to process the explicit route stops, PLUS the final return to depot.
        # Let's construct a list of targets.
        targets = list(route)
        
        # If the last target is NOT depot, imply a return to depot.
        if targets and targets[-1] != depot:
            targets.append(depot)
            
        for next_loc in targets:
            # Calculate distance to next target
            dist = current_loc.distance_to(next_loc)
            
            # Check fuel
            if dist <= current_fuel:
                # Can reach
                # Add to final route (unless it's the implicit final depot? 
                # If we want explicit route, we add everything.
                # But typically we don't duplicate implicit start depot.
                # Intermediate depots: YES.
                # Final depot: YES (explicit closing).
                
                final_route.append(next_loc)
                total_dist += dist
                current_fuel -= dist
                current_loc = next_loc
                
                # If we just arrived at Depot, Refuel!
                if current_loc == depot:
                    current_fuel = vehicle.max_distance
                    
            else:
                # Need fuel
                reachable_stations = [g for g in gas_stations if current_loc.distance_to(g) <= current_fuel]
                
                if not reachable_stations:
                    feasible = False
                    final_route.append(next_loc)
                    total_dist += dist
                    current_loc = next_loc
                    current_fuel = 0
                    if current_loc == depot: current_fuel = vehicle.max_distance
                else:
                    best_station = min(reachable_stations, key=lambda g: g.distance_to(next_loc))
                    
                    # Go to station
                    d1 = current_loc.distance_to(best_station)
                    final_route.append(best_station)
                    total_dist += d1
                    
                    # Refuel
                    current_fuel = vehicle.max_distance
                    current_loc = best_station
                    
                    # Go to target
                    d2 = best_station.distance_to(next_loc)
                    if d2 > current_fuel:
                         feasible = False
                    
                    final_route.append(next_loc)
                    total_dist += d2
                    current_fuel -= d2
                    current_loc = next_loc
                    
                    if current_loc == depot:
                        current_fuel = vehicle.max_distance

        return final_route, total_dist, feasible

    @staticmethod
    def calculate_priority_score(routes: List[List[Location]]) -> float:
        score = 0.0
        for route in routes:
            for i, loc in enumerate(route):
                # Only penalize deliveries
                if getattr(loc, 'type', 'delivery') == 'delivery':
                    score += (i + 1) * (loc.priority ** 2)
        return score
