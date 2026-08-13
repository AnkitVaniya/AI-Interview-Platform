"""
Topic dependency graph, modeled as a DAG. Topological sort gives a valid
overall learning order; given a user's mastered topics, we can compute
which topics are now "unlocked" (all prerequisites satisfied).
"""
from collections import defaultdict, deque

# adjacency: prerequisite -> [topics that depend on it]
TOPIC_DEPENDENCIES: dict[str, list[str]] = {
    "Arrays": ["Strings", "Two Pointers", "Hashing"],
    "Strings": ["Two Pointers"],
    "Two Pointers": ["Sliding Window"],
    "Hashing": ["Sliding Window", "Graphs"],
    "Sliding Window": ["Dynamic Programming"],
    "Recursion": ["Trees", "Backtracking"],
    "Trees": ["Graphs", "Dynamic Programming"],
    "Graphs": ["Dynamic Programming"],
    "Backtracking": [],
    "Dynamic Programming": [],
}


class TopicGraph:
    def __init__(self, dependencies: dict[str, list[str]] = TOPIC_DEPENDENCIES):
        self.adjacency = dependencies
        self.all_topics = self._collect_all_topics()

    def _collect_all_topics(self) -> set[str]:
        topics = set(self.adjacency.keys())
        for deps in self.adjacency.values():
            topics.update(deps)
        return topics

    def topological_order(self) -> list[str]:
        """Kahn's algorithm — returns a valid overall study order."""
        in_degree = {t: 0 for t in self.all_topics}
        for prereq, dependents in self.adjacency.items():
            for d in dependents:
                in_degree[d] += 1

        queue = deque(sorted([t for t, deg in in_degree.items() if deg == 0]))
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for dependent in sorted(self.adjacency.get(node, [])):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(self.all_topics):
            raise ValueError("Cycle detected in topic dependency graph")
        return order

    def unlocked_topics(self, mastered_topics: set[str]) -> list[str]:
        """Topics whose every prerequisite is already mastered, excluding already-mastered ones."""
        prereqs_of = defaultdict(list)
        for prereq, dependents in self.adjacency.items():
            for d in dependents:
                prereqs_of[d].append(prereq)

        unlocked = []
        for topic in self.all_topics:
            if topic in mastered_topics:
                continue
            required = prereqs_of.get(topic, [])
            if all(r in mastered_topics for r in required):
                unlocked.append(topic)
        return sorted(unlocked)


topic_graph = TopicGraph()
