import unittest
from src.models.location import Location
from src.models.vehicle import Vehicle
from src.utils.vrp_helper import VRPHelper
from src.algorithms.genetic_optimizer import GeneticOptimizer

class TestTSP(unittest.TestCase):
    def setUp(self):
        self.depot = Location(0, 0, 0, "Depot")
        self.loc1 = Location(1, 10, 0, "L1", demand=5)
        self.loc2 = Location(2, 20, 0, "L2", demand=6)
        self.loc3 = Location(3, 30, 0, "L3", demand=5)
        
    def test_distance(self):
        self.assertEqual(self.depot.distance_to(self.loc1), 10.0)

    def test_split_route(self):
        tour = [self.loc1, self.loc2, self.loc3]
        locations = [self.loc1, self.loc2, self.loc3]
        fleet = [Vehicle(1, 10, max_distance=100), Vehicle(2, 10, max_distance=100), Vehicle(3, 10, max_distance=100)]
        
        # Instantiate Optimizer to build the matrix and lookups
        ga = GeneticOptimizer(locations, self.depot, fleet=fleet, population_size=10, generations=1)
        
        # Manually invoke the fitness function logic to test splitting
        # We need the indices of the tour
        tour_indices = [ga.id_map[loc.id] for loc in tour]
        
        routes_ids, dist, unassigned = VRPHelper.split_route_fleet(
            tuple(tour_indices), 
            ga.depot_idx, 
            ga.fleet_specs, 
            ga.gas_station_indices, 
            ga.distance_matrix, 
            ga.demands
        )
        
        # fleet_specs should be length 3, so 3 routes are created (some might be empty)
        self.assertEqual(len(routes_ids), 3)
        self.assertEqual(unassigned, 0)

    def test_ga_runs(self):
        locations = [self.loc1, self.loc2, self.loc3]
        fleet = [Vehicle(i, 10, max_distance=100) for i in range(5)]
        ga = GeneticOptimizer(locations, self.depot, fleet=fleet, generations=5, population_size=10)
        routes, dist, history = ga.run()
        self.assertTrue(len(routes) > 0)
        self.assertTrue(dist > 0)
        self.assertTrue(len(history) == 5)

    def test_ga_early_stopping(self):
        locations = [self.loc1, self.loc2, self.loc3]
        fleet = [Vehicle(i, 10, max_distance=100) for i in range(5)]
        ga = GeneticOptimizer(locations, self.depot, fleet=fleet, generations=50, population_size=10, early_stopping_rounds=2)
        routes, dist, history = ga.run()
        self.assertTrue(len(history) < 50)

if __name__ == '__main__':
    unittest.main()
