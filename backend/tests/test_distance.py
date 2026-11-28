import unittest
from dairy_core.routing.distance import build_distance_matrix, haversine_km


class TestDistanceModule(unittest.TestCase):
    def test_same_point_is_zero(self):
        pt = (27.7172, 85.3240)
        self.assertAlmostEqual(haversine_km(pt, pt), 0.0, places=9)

    def test_equator_one_degree_latitude(self):
        # 1 degree of latitude is ~111.19 km
        d = haversine_km((0.0, 0.0), (1.0, 0.0))
        self.assertAlmostEqual(d, 111.19, delta=0.2)

    def test_matrix_invariants_and_override(self):
        # Synthetic test points (clearly labeled, not real pins)
        pts = [
            (27.7172, 85.3240),  # 0: synthetic depot
            (27.7150, 85.3123),  # 1: synthetic cafe A
            (27.7215, 85.3285),  # 2: synthetic cafe B
        ]
        mat = build_distance_matrix(pts, road_factor=1.3, overrides={(0, 2): 2.5})

        self.assertEqual(len(mat), 3)
        for i in range(3):
            self.assertEqual(mat[i][i], 0.0)
            for j in range(3):
                self.assertGreaterEqual(mat[i][j], 0.0)
                self.assertAlmostEqual(mat[i][j], mat[j][i], places=9)

        # Override wins over estimate in both directions
        self.assertAlmostEqual(mat[0][2], 2.5)
        self.assertAlmostEqual(mat[2][0], 2.5)

    def test_missing_coordinates_fail_loudly(self):
        with self.assertRaises(ValueError):
            build_distance_matrix([(27.71, 85.32), None])


if __name__ == "__main__":
    unittest.main()