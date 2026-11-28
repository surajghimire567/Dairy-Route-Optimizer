import math
from typing import Dict, List, Optional, Sequence, Tuple

EARTH_RADIUS_KM = 6371.0

Point = Tuple[float, float]  # (latitude, longitude) in decimal degrees
PairOverride = Dict[Tuple[int, int], float]


def haversine_km(point_a: Point, point_b: Point) -> float:
    """
    Calculate great-circle straight-line distance in km between two (lat, lng) points
    in decimal degrees using Earth radius R = 6,371 km.
    """
    lat1, lon1 = point_a
    lat2, lon2 = point_b

    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    # Clamp 'a' to [0.0, 1.0] to guard against floating-point overshoot (e.g. 1.0000000000000002)
    a = min(1.0, max(0.0, a))
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def build_distance_matrix(
    points: Sequence[Optional[Point]],
    road_factor: float = 1.3,
    overrides: Optional[PairOverride] = None,
) -> List[List[float]]:
    """
    Build a symmetric (n x n) distance matrix in kilometres.
    - Index 0 must be the dairy depot; indices 1..n-1 are the stops.
    - Each pair defaults to haversine_km(a, b) * road_factor.
    - Verified road distances in `overrides` (e.g., {(0, 1): 4.2}) override the estimate
      symmetrically for both (i, j) and (j, i).
    """
    if not points:
        raise ValueError("points must include at least the depot at index 0.")
    if road_factor <= 0:
        raise ValueError("road_factor must be positive.")

    # Validate that every requested point has both lat and lng before computing
    for idx, pt in enumerate(points):
        if pt is None or pt[0] is None or pt[1] is None:
            raise ValueError(
                f"Missing GPS coordinates for node {idx}. "
                "Verify coordinates before building the real-data distance matrix."
            )

    n = len(points)
    matrix: List[List[float]] = [[0.0] * n for _ in range(n)]
    pair_overrides = overrides or {}

    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in pair_overrides:
                dist = float(pair_overrides[(i, j)])
            elif (j, i) in pair_overrides:
                dist = float(pair_overrides[(j, i)])
            else:
                dist = haversine_km(points[i], points[j]) * road_factor

            if dist < 0:
                raise ValueError(f"Distance between node {i} and {j} cannot be negative.")

            matrix[i][j] = dist
            matrix[j][i] = dist

    return matrix