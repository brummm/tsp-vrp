import random
import copy
from typing import List, Tuple
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper

class GeneticOptimizer:
    def __init__(self, locations: List[Location], depot: Location, fleet: List[Vehicle], 
                 pop_size=100, elite_size=2, mutation_rate=0.02, generations=200,
                 early_stopping_rounds: int = None, priority_weight: float = 0.1):
        self.deliveries = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'delivery']
        self.gas_stations = [loc for loc in locations if getattr(loc, 'type', 'delivery') == 'gas_station']
        
        self.depot = depot
        self.fleet = fleet
        self.pop_size = pop_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.early_stopping_rounds = early_stopping_rounds
        self.priority_weight = priority_weight

    def initial_population(self) -> List[List[Location]]:
        population = []
        for _ in range(self.pop_size):
            ind = self.deliveries[:]
            random.shuffle(ind)
            population.append(ind)
        return population

    def fitness(self, individual: List[Location]) -> float:
        routes, total_dist, unassigned_count = VRPHelper.split_route_fleet(individual, self.depot, self.fleet, self.gas_stations)
        
        unassigned_penalty = unassigned_count * 50000.0
        priority_penalty = VRPHelper.calculate_priority_score(routes) * self.priority_weight
        
        return total_dist + unassigned_penalty + priority_penalty

    def selection_tournament(self, population: List[List[Location]], k=5) -> List[Location]:
        tournament = random.sample(population, k)
        return min(tournament, key=self.fitness)

    def crossover_ordered(self, p1: List[Location], p2: List[Location]) -> List[Location]:
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

    def run(self) -> Tuple[List[List[Location]], float, List[float]]:
        pop = self.initial_population()
        best_overall_ind = None
        best_overall_fit = float('inf')
        fitness_history = []
        no_improvement_count = 0
        
        for gen in range(self.generations):
            pop.sort(key=self.fitness)
            
            current_best_fit = self.fitness(pop[0])
            fitness_history.append(current_best_fit)
            
            if current_best_fit < best_overall_fit:
                best_overall_fit = current_best_fit
                best_overall_ind = list(pop[0])
                no_improvement_count = 0
            else:
                no_improvement_count += 1
                
            if self.early_stopping_rounds and no_improvement_count >= self.early_stopping_rounds:
                print(f"Stopping early at generation {gen} due to no improvement for {no_improvement_count} rounds.")
                break
            
            new_pop = pop[:self.elite_size]
            while len(new_pop) < self.pop_size:
                p1 = self.selection_tournament(pop)
                p2 = self.selection_tournament(pop)
                child = self.crossover_ordered(p1, p2)
                child = self.mutate_swap(child)
                new_pop.append(child)
            pop = new_pop
        
        # Reconstruct best solution
        final_routes, total_dist, unassigned = VRPHelper.split_route_fleet(best_overall_ind, self.depot, self.fleet, self.gas_stations)
        
        return final_routes, total_dist, fitness_history
