import random
import copy
from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper

class GeneticOptimizer:
    def __init__(self, locations: List[Location], depot: Location, fleet: List[Vehicle], 
                 pop_size=100, elite_size=2, mutation_rate=0.02, generations=200):
        # Separate deliveries from gas stations
        self.deliveries = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'delivery']
        self.gas_stations = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'gas_station']
        
        self.depot = depot
        self.fleet = fleet
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations

    def initial_population(self) -> List[List[Location]]:
        population = []
        for _ in range(self.pop_size):
            ind = self.deliveries[:]
            random.shuffle(ind)
            population.append(ind)
        return population

    def fitness(self, individual: List[Location]) -> float:
        """
        Calculates fitness. Lower is better.
        """
        raw_routes, unassigned = VRPHelper.split_route_fleet(individual, self.depot, self.fleet)
        
        total_dist = 0.0
        infeasible_penalty = 0.0
        processed_routes = []

        for idx, route in enumerate(raw_routes):
            vehicle = self.fleet[idx]
            proc_route, dist, feasible = VRPHelper.process_route_refueling(route, vehicle, self.depot, self.gas_stations)
            total_dist += dist
            if not feasible:
                infeasible_penalty += 50000.0 # Huge penalty for getting stranded
            processed_routes.append(proc_route)

        unassigned_penalty = len(unassigned) * 10000.0
        priority_penalty = VRPHelper.calculate_priority_score(processed_routes) * 0.1
        
        return total_dist + unassigned_penalty + infeasible_penalty + priority_penalty

    def selection_tournament(self, population: List[List[Location]], k=5) -> List[Location]:
        tournament = random.sample(population, k)
        return min(tournament, key=self.fitness)

    def crossover_ordered(self, p1: List[Location], p2: List[Location]) -> List[Location]:
        # OX1 Crossover
        if len(p1) < 2: return p1
        
        start, end = sorted(random.sample(range(len(p1)), 2))
        child = [None] * len(p1)
        child[start:end] = p1[start:end]
        
        current_p2_idx = 0
        for i in range(len(child)):
            if child[i] is None:
                while p2[current_p2_idx] in child:
                    current_p2_idx += 1
                    if current_p2_idx >= len(p2): break
                if current_p2_idx < len(p2):
                    child[i] = p2[current_p2_idx]
        
        remaining = [x for x in p1 if x not in child]
        for i in range(len(child)):
            if child[i] is None:
                child[i] = remaining.pop(0)
                
        return child

    def mutate_swap(self, individual: List[Location]) -> List[Location]:
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                j = random.randint(0, len(individual) - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual

    def run(self) -> Tuple[List[List[Location]], float]:
        pop = self.initial_population()
        best_overall_ind = None
        best_overall_fit = float('inf')
        
        for gen in range(self.generations):
            pop.sort(key=self.fitness)
            
            if self.fitness(pop[0]) < best_overall_fit:
                best_overall_fit = self.fitness(pop[0])
                best_overall_ind = list(pop[0])
            
            new_pop = pop[:self.elite_size]
            
            while len(new_pop) < self.pop_size:
                p1 = self.selection_tournament(pop)
                p2 = self.selection_tournament(pop)
                child = self.crossover_ordered(p1, p2)
                child = self.mutate_swap(child)
                new_pop.append(child)
            
            pop = new_pop
        
        # Reconstruct best solution
        raw_routes, unassigned = VRPHelper.split_route_fleet(best_overall_ind, self.depot, self.fleet)
        
        final_routes = []
        total_dist = 0.0
        
        for idx, route in enumerate(raw_routes):
            vehicle = self.fleet[idx]
            proc_route, dist, feasible = VRPHelper.process_route_refueling(route, vehicle, self.depot, self.gas_stations)
            final_routes.append(proc_route)
            total_dist += dist
            
        return final_routes, total_dist