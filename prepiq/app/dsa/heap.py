"""
Custom max-heap for leaderboard ranking, built from scratch (not heapq)
specifically so the DSA mechanics are visible and explainable in an interview.
Ranks by score descending; ties broken by earlier submission time.
"""
from dataclasses import dataclass, field


@dataclass
class LeaderboardEntry:
    user_id: int
    user_name: str
    score: float
    last_submission_ts: float  # unix timestamp — earlier is better on ties


class MaxHeap:
    def __init__(self):
        self._heap: list[LeaderboardEntry] = []

    def _is_higher_priority(self, a: LeaderboardEntry, b: LeaderboardEntry) -> bool:
        # a should rank above b: higher score wins, earlier timestamp wins ties
        if a.score != b.score:
            return a.score > b.score
        return a.last_submission_ts < b.last_submission_ts

    def push(self, entry: LeaderboardEntry) -> None:
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._is_higher_priority(self._heap[i], self._heap[parent]):
                self._heap[i], self._heap[parent] = self._heap[parent], self._heap[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._heap)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            highest = i
            if left < n and self._is_higher_priority(self._heap[left], self._heap[highest]):
                highest = left
            if right < n and self._is_higher_priority(self._heap[right], self._heap[highest]):
                highest = right
            if highest == i:
                break
            self._heap[i], self._heap[highest] = self._heap[highest], self._heap[i]
            i = highest

    def pop_top(self) -> LeaderboardEntry | None:
        if not self._heap:
            return None
        top = self._heap[0]
        last = self._heap.pop()
        if self._heap:
            self._heap[0] = last
            self._sift_down(0)
        return top

    def top_n(self, n: int) -> list[LeaderboardEntry]:
        """Non-destructive: returns top n without mutating the heap."""
        import copy

        temp = copy.deepcopy(self)
        result = []
        for _ in range(min(n, len(temp._heap))):
            result.append(temp.pop_top())
        return result


def build_leaderboard(entries: list[LeaderboardEntry], top_n: int = 10) -> list[LeaderboardEntry]:
    heap = MaxHeap()
    for entry in entries:
        heap.push(entry)
    return heap.top_n(top_n)
