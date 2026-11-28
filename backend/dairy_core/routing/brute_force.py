from itertools import permutations
from typing import List, Sequence, Tuple

from .base import RouteSolver

MAX_BRUTE_FORCE_STOPS = 9


class BruteForceSolver(RouteSolver):
    """
    Exact small-instance checker (capped at n <= 9 stops).
    Evaluates all n! permutations for an OPEN PATH starting at depot 0:
    0 -> s1 -> s2 -> ... -> sn (no return leg back to 0).
    """

    def solve(self, distance_matrix: Sequence[Sequence[float]]) -> Tuple[List[int], float]:
        n_nodes = len(distance_matrix)
        if n_nodes == 0:
            raise ValueError("Distance matrix cannot be empty.")

        # Validate square matrix and non-negative entries
        for row in distance_matrix:
            if len(row) != n_nodes:
                raise ValueError("Distance matrix must be square.")
            if any(val < 0 for val in row):
                raise ValueError("Distance matrix cannot contain negative distances.")

        n_stops = n_nodes - 1
        if n_stops == 0:
            return [0], 0.0

        if n_stops > MAX_BRUTE_FORCE_STOPS:
            raise ValueError(
                f"BruteForceSolver supports at most {MAX_BRUTE_FORCE_STOPS} stops (got {n_stops})."
            )

        best_cost = float("inf")
        best_perm: Tuple[int, ...] = ()

        # itertools.permutations yields tuples in lexicographical order,
        # so strict `<` deterministically breaks ties in favor of the lexicographically smallest route.
        for perm in permutations(range(1, n_nodes)):
            total = distance_matrix[0][perm[0]]
            for idx in range(len(perm) - 1):
                total += distance_matrix[perm[idx]][perm[idx + 1]]

            if total < best_cost:
                best_cost = total
                best_perm = perm

        order = [0, *best_perm]
        return order, float(best_cost)