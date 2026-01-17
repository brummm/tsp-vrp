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
        # Capacity 10. L1(5), L2(6), L3(5).
        # Our greedy split is sequential.
        # [L1] -> load 5. Next L2(6) -> 5+6=11 > 10. Split.
        # Route 1: [L1]. New load 6.
        # Next L3(5) -> 6+5=11 > 10. Split.
        # Route 2: [L2]. New load 5.
        # Route 3: [L3].
        tour = [self.loc1, self.loc2, self.loc3]
        routes = VRPHelper.split_route(tour, self.depot, 10)
        self.assertEqual(len(routes), 3)
        self.assertEqual(routes[0], [self.loc1])
        self.assertEqual(routes[1], [self.loc2])

    def test_ga_runs(self):
        locations = [self.loc1, self.loc2, self.loc3]
        vehicle = Vehicle(id=1, capacity=10, max_distance=100)
        ga = GeneticOptimizer(locations, self.depot, vehicle=vehicle, generations=5, pop_size=10)
        routes, dist = ga.run()
        self.assertTrue(len(routes) > 0)
        self.assertTrue(dist > 0)

if __name__ == '__main__':
    unittest.main()
