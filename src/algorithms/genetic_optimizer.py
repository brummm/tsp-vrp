import random
import copy
from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper

class GeneticOptimizer:
    def __init__(self, locations: List[Location], depot: Location, vehicle: Vehicle, 
                 pop_size=100, elite_size=2, mutation_rate=0.02, generations=200):
        self.locations = locations
        self.depot = depot
        self.vehicle = vehicle
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations

    def initial_population(self) -> List[List[Location]]:
        population = []
        for _ in range(self.pop_size):
            ind = self.locations[:]
            random.shuffle(ind)
            population.append(ind)
        return population

    def fitness(self, individual: List[Location]) -> float:
        """
        Calculates fitness. Lower is better.
        Combines Distance + Priority Penalty + Max Distance Penalty.
        """
        routes = VRPHelper.split_route(individual, self.depot, self.vehicle.capacity)
        
        total_dist = 0.0
        max_dist_penalty = 0.0
        
        for route in routes:
            r_dist = VRPHelper.calculate_route_distance(route, self.depot)
            total_dist += r_dist
            if r_dist > self.vehicle.max_distance:
                # Penalty: Excess distance * large factor
                max_dist_penalty += (r_dist - self.vehicle.max_distance) * 1000.0

        # Priority penalty could be added here, but for 'Otimização de Rotas' distance is key.
        # We can add a small weight for priority to break ties or favor better ordering.
        priority_penalty = VRPHelper.calculate_priority_score(routes) * 0.1
        
        return total_dist + priority_penalty + max_dist_penalty

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
        
        # Fallback if None remains (should not happen with correct logic but safe for robustness)
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
                best_overall_ind = list(pop[0]) # Copy
            
            new_pop = pop[:self.elite_size]
            
            while len(new_pop) < self.pop_size:
                p1 = self.selection_tournament(pop)
                p2 = self.selection_tournament(pop)
                child = self.crossover_ordered(p1, p2)
                child = self.mutate_swap(child)
                new_pop.append(child)
            
            pop = new_pop
            
            # Optional: print progress every 50 gens
            # if gen % 50 == 0:
            #     print(f"Gen {gen}: {best_overall_fit}")

        best_routes = VRPHelper.split_route(best_overall_ind, self.depot, self.vehicle.capacity)
        best_dist = VRPHelper.calculate_total_distance(best_routes, self.depot)
        
        return best_routes, best_dist
