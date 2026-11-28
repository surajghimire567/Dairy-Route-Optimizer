from abc import ABC, abstractmethod
from typing import List, Sequence, Tuple


class RouteSolver(ABC):
    @abstractmethod
    def solve(self, distance_matrix: Sequence[Sequence[float]]) -> Tuple[List[int], float]:
        """
        Given a symmetric (N x N) distance matrix where index 0 is the dairy depot
        and indices 1..N-1 are today's stops, return (order, total_km).
        For an open path, `order` is [0, s1, s2, ..., sn].
        """
        raise NotImplementedError