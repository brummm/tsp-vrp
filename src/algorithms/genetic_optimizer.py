import random
import copy
from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper

class GeneticOptimizer:
    def __init__(self, locations: List[Location], depot: Location, fleet: List[Vehicle], 
                 population_size=100, elite_size=2, mutation_rate=0.02, generations=200,
                 early_stopping_rounds: int = None, priority_weight: float = 0.1):
        self.deliveries = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'delivery']
        self.gas_stations = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'gas_station']
        
        self.depot = depot
        self.fleet = fleet
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.early_stopping_rounds = early_stopping_rounds
        self.priority_weight = priority_weight

    def run(self) -> Tuple[List[List[Location]], float, List[float]]:
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
        
        # Reconstruct best solution
        final_routes, total_dist, unassigned = VRPHelper.split_route_fleet(best_overall_individual, self.depot, self.fleet, self.gas_stations)
        
        return final_routes, total_dist, fitness_history
    

    def initial_population(self) -> List[List[Location]]:
        population = []
        for _ in range(self.population_size):
            individual = self.deliveries[:]
            random.shuffle(individual)
            population.append(individual)
        return population

    def fitness(self, individual: List[Location]) -> float:
        routes, total_dist, unassigned_count = VRPHelper.split_route_fleet(individual, self.depot, self.fleet, self.gas_stations)
        
        unassigned_penalty = unassigned_count * 50000.0 # add a huge penalty if a route is not complete
        priority_penalty = VRPHelper.calculate_priority_score(routes) * self.priority_weight # adds an adjustable penalty to try to 
        
        return total_dist + unassigned_penalty + priority_penalty

    def selection_tournament(self, population: List[List[Location]], k=5) -> List[Location]:
        tournament = random.sample(population, k)
        return min(tournament, key=self.fitness)

    def crossover_ordered(self, parent1: List[Location], parent2: List[Location]) -> List[Location]:
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

    def mutate_swap(self, individual: List[Location]) -> List[Location]:
        for i in range(len(individual)):
            if random.random() < self.mutation_rate:
                j = random.randint(0, len(individual) - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual

    