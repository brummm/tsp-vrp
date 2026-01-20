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
        fleet = [Vehicle(1, 10, max_distance=100), Vehicle(2, 10, max_distance=100), Vehicle(3, 10, max_distance=100)]
        gas_stations = []
        
        # Logic: Chunking
        # 3 vehicles, 3 locs. 1 loc each.
        # All reachable.
        routes, dist, unassigned = VRPHelper.split_route_fleet(tour, self.depot, fleet, gas_stations)
        
        self.assertEqual(len(routes), 3)
        self.assertEqual(routes[0], [self.loc1, self.depot])
        self.assertEqual(routes[1], [self.loc2, self.depot])
        self.assertEqual(routes[2], [self.loc3, self.depot])
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
