import unittest
from dairy_core.routing.brute_force import BruteForceSolver


class TestBruteForceOpenPath(unittest.TestCase):
    def setUp(self):
        self.solver = BruteForceSolver()
        # Worked 4-stop matrix from Section 7 (node 0 = dairy)
        self.four_stop_matrix = [
            [0, 8, 10, 11, 12],
            [8, 0, 10, 7, 9],
            [10, 10, 0, 7, 12],
            [11, 7, 7, 0, 5],
            [12, 9, 12, 5, 0],
        ]

    def test_four_stop_open_path_optimum(self):
        order, total_km = self.solver.solve(self.four_stop_matrix)
        self.assertEqual(order, [0, 2, 1, 3, 4])
        self.assertAlmostEqual(total_km, 32.0, places=9)

    def test_route_validity_and_recomputation(self):
        order, reported_km = self.solver.solve(self.four_stop_matrix)
        # Starts at depot 0, does not return to 0, visits stops 1..4 exactly once
        self.assertEqual(order[0], 0)
        self.assertEqual(sorted(order[1:]), [1, 2, 3, 4])

        # Recompute distance independently from matrix
        recomputed = sum(
            self.four_stop_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1)
        )
        self.assertAlmostEqual(reported_km, recomputed, places=9)

    def test_zero_stops_returns_depot_only(self):
        order, total_km = self.solver.solve([[0.0]])
        self.assertEqual(order, [0])
        self.assertEqual(total_km, 0.0)

    def test_rejects_more_than_9_stops_and_malformed_matrix(self):
        # 10 stops -> 11x11 matrix
        big_matrix = [[0.0] * 11 for _ in range(11)]
        with self.assertRaises(ValueError):
            self.solver.solve(big_matrix)

        # Non-square matrix
        with self.assertRaises(ValueError):
            self.solver.solve([[0.0, 1.0], [1.0]])


if __name__ == "__main__":
    unittest.main()