from typing import List
from src.models.location import Location

class VRPHelper:
    @staticmethod
    def split_route(tour: List[Location], depot: Location, vehicle_capacity: int) -> List[List[Location]]:
        """
        Splits a single TSP tour into multiple vehicle routes based on capacity.
        This allows solving VRP using standard TSP permutation chromosomes.
        """
        routes = []
        current_route = []
        current_load = 0

        for loc in tour:
            if current_load + loc.demand <= vehicle_capacity:
                current_route.append(loc)
                current_load += loc.demand
            else:
                if current_route:
                    routes.append(current_route)
                current_route = [loc]
                current_load = loc.demand
        
        if current_route:
            routes.append(current_route)
            
        return routes

    @staticmethod
    def calculate_total_distance(routes: List[List[Location]], depot: Location) -> float:
        """
        Calculates total fleet distance including return to depot.
        """
        total_dist = 0.0
        for route in routes:
            if not route: continue
            # Depot -> First
            total_dist += depot.distance_to(route[0])
            # Inter-nodes
            for i in range(len(route) - 1):
                total_dist += route[i].distance_to(route[i+1])
            # Last -> Depot
            total_dist += route[-1].distance_to(depot)
        return total_dist

    @staticmethod
    def calculate_priority_score(routes: List[List[Location]]) -> float:
        """
        Calculates a score based on priority. Higher is worse (late delivery of high priority).
        Simple heuristic: sum of (index_in_route * priority).
        """
        score = 0.0
        for route in routes:
            for i, loc in enumerate(route):
                # 1=Normal, 2=High, 3=Critical.
                # We want Critical to be delivered early (low i).
                # Penalty = index * priority^2
                score += (i + 1) * (loc.priority ** 2)
        return score
