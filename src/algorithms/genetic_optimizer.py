import random
import copy
from typing import List, Tuple, Dict
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper

class GeneticOptimizer:
    def __init__(self, locations: List[Location], depot: Location, fleet: List[Vehicle], 
                 population_size=100, elite_size=2, mutation_rate=0.02, generations=200,
                 early_stopping_rounds: int = None, priority_weight: float = 0.1):
        
        # --- Pre-processing for Performance (Data-Oriented Design) ---
        self.all_locations = locations + [depot]
        # Normalize IDs to 0..N-1 range for array indexing
        # Mapping: old_id -> new_index
        self.id_map = {loc.id: i for i, loc in enumerate(self.all_locations)}
        self.reverse_map = {i: loc for i, loc in enumerate(self.all_locations)}
        
        self.num_locations = len(self.all_locations)
        
        # Arrays for O(1) lookup
        self.demands = [0] * self.num_locations
        self.priorities = [0] * self.num_locations
        self.types = [""] * self.num_locations
        
        for i, loc in enumerate(self.all_locations):
            self.demands[i] = loc.demand
            self.priorities[i] = loc.priority
            self.types[i] = getattr(loc, 'type', 'delivery')

        # Identify special indices
        self.depot_idx = self.id_map[depot.id]
        self.delivery_indices = [self.id_map[loc.id] for loc in locations if getattr(loc, 'type', 'delivery') == 'delivery']
        self.gas_station_indices = [self.id_map[loc.id] for loc in locations if getattr(loc, 'type', 'delivery') == 'gas_station']
        
        # Fleet Specs (Tuple for immutability)
        self.fleet_specs = [(v.capacity, v.max_distance) for v in fleet]
        
        # Distance Matrix (List of Lists)
        self.distance_matrix = [[0.0] * self.num_locations for _ in range(self.num_locations)]
        for i in range(self.num_locations):
            for j in range(self.num_locations):
                if i != j:
                    loc_a = self.reverse_map[i]
                    loc_b = self.reverse_map[j]
                    self.distance_matrix[i][j] = loc_a.distance_to(loc_b)

        # Config
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.early_stopping_rounds = early_stopping_rounds
        self.priority_weight = priority_weight

    def run(self) -> Tuple[List[List[Location]], float, List[float]]:
        # Run Genetic Algorithm using Integers
        population = self.initial_population()
        best_overall_individual = None
        best_overall_fitness = float('inf')
        fitness_history = []
        no_improvement_count = 0
        
        for generation in range(self.generations):
            population.sort(key=self.fitness)
            
            current_best_fitness = self.fitness(population[0])
            fitness_history.append(current_best_fitness)
            
            if current_best_fitness < best_overall_fitness:
                best_overall_fitness = current_best_fitness
                best_overall_individual = list(population[0])
                no_improvement_count = 0
            else:
                no_improvement_count += 1
                
            if self.early_stopping_rounds and no_improvement_count >= self.early_stopping_rounds:
                print(f"Stopping early at generation {generation} due to no improvement for {no_improvement_count} rounds.")
                break
            
            new_population = population[:self.elite_size]
            while len(new_population) < self.population_size:
                parent1 = self.selection_tournament(population)
                parent2 = self.selection_tournament(population)
                child = self.crossover_ordered(parent1, parent2)
                child = self.mutate_swap(child)
                new_population.append(child)
            population = new_population
        
        # Reconstruct Objects from Best Integer Individual
        # 1. Get the integer routes
        final_route_ids, total_dist, unassigned = VRPHelper.split_route_fleet(
            tuple(best_overall_individual), 
            self.depot_idx, 
            self.fleet_specs, 
            self.gas_station_indices, 
            self.distance_matrix,
            self.demands
        )
        
        # 2. Convert IDs back to Location Objects
        final_routes_objs = []
        for route_ids in final_route_ids:
            route_objs = [self.reverse_map[idx] for idx in route_ids]
            final_routes_objs.append(route_objs)
            
        return final_routes_objs, total_dist, fitness_history
    

    def initial_population(self) -> List[List[int]]:
        population = []
        
        # 1. Greedy Individual (Matrix Lookup)
        greedy_individual = []
        unvisited = self.delivery_indices[:]
        current_idx = self.depot_idx
        
        while unvisited:
            # Fast matrix lookup
            next_idx = min(unvisited, key=lambda idx: self.distance_matrix[current_idx][idx])
            greedy_individual.append(next_idx)
            unvisited.remove(next_idx)
            current_idx = next_idx
            
        population.append(greedy_individual)
        
        # 2. Random Individuals
        for _ in range(self.population_size - 1):
            individual = self.delivery_indices[:]
            random.shuffle(individual)
            population.append(individual)
            
        return population

    def fitness(self, individual: List[int]) -> float:
        # Pass Tuple(individual) for memoization key
        routes, total_dist, unassigned_count = VRPHelper.split_route_fleet(
            tuple(individual), 
            self.depot_idx, 
            self.fleet_specs, 
            self.gas_station_indices, 
            self.distance_matrix,
            self.demands
        )
        
        unassigned_penalty = unassigned_count * 50000.0
        priority_penalty = VRPHelper.calculate_priority_score(routes, self.priorities) * self.priority_weight
        
        return total_dist + unassigned_penalty + priority_penalty

    def selection_tournament(self, population: List[List[int]], k=5) -> List[int]:
        tournament = random.sample(population, k)
        return min(tournament, key=self.fitness)

    def crossover_ordered(self, parent1: List[int], parent2: List[int]) -> List[int]:
        if len(parent1) < 2: return parent1
        start, end = sorted(random.sample(range(len(parent1)), 2))
        child = [None] * len(parent1)
        child[start:end] = parent1[start:end]
        
        current_parent2_idx = 0
        for i in range(len(child)):
            if child[i] is None:
                while parent2[current_parent2_idx] in child:
                    current_parent2_idx += 1
                    if current_parent2_idx >= len(parent2): break
                if current_parent2_idx < len(parent2):
                    child[i] = parent2[current_parent2_idx]
        
        remaining = [x for x in parent1 if x not in child]
        for i in range(len(child)):
            if child[i] is None:
                child[i] = remaining.pop(0)
        return child

    def mutate_swap(self, individual: List[int]) -> List[int]:
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                j = random.randint(0, len(individual) - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual