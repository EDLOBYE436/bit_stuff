# dijkstra_teaching.py
import heapq
from typing import Dict, List, Tuple, Any

Graph = Dict[Any, List[Tuple[Any, float]]]
# Example graph form:
# graph = {
#   'A': [('B', 1), ('C', 4)],
#   'B': [('C', 2), ('D', 5)],
#    ...
# }

def dijkstra(graph: Graph, source: Any) -> Tuple[Dict[Any, float], Dict[Any, Any]]:
    """
    Compute shortest distances from `source` to every node in `graph`.
    Returns:
      - dist: dict mapping node -> shortest distance (float('inf') if unreachable)
      - prev: dict mapping node -> predecessor on shortest path (None if none)
    """
    # 1) Initialization
    dist = {node: float('inf') for node in graph}   # tentative distances
    prev = {node: None for node in graph}           # predecessors
    dist[source] = 0.0

    # Priority queue stores pairs (distance, node)
    heap: List[Tuple[float, Any]] = [(0.0, source)]

    # 2) Main loop: pop smallest tentative distance and relax neighbors
    while heap:
        current_dist, u = heapq.heappop(heap)

        # 2.1) Skip stale heap entries: if we popped an old distance, ignore it.
        if current_dist > dist[u]:
            continue

        # 2.2) Explore neighbors
        for v, weight in graph[u]:
            # Dijkstra does not allow negative weights - guard here for clarity
            if weight < 0:
                raise ValueError("Graph contains negative edge weight; Dijkstra is not valid.")

            alt = dist[u] + weight  # potential new distance to v via u

            # 2.3) If we found a better path to v, update and push to heap
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))

    return dist, prev

def reconstruct_path(prev: Dict[Any, Any], target: Any) -> List[Any]:
    """Reconstruct path from source to target using prev map. Returns empty list if unreachable."""
    if prev.get(target) is None and target not in prev:
        # target not in graph
        return []
    path = []
    node = target
    # If dist[target] may be inf, this will still produce a chain of Nones -> just check result
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path

# ------------------------------
# Example usage and demonstration
# ------------------------------
if __name__ == "__main__":
    example_graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1), ('E', 7)],
        'D': [('B', 5), ('C', 1), ('E', 3)],
        'E': [('D', 3), ('C', 7)]
    }

    source = 'A'
    dist, prev = dijkstra(example_graph, source)

    print("Shortest distances from", source)
    for node in sorted(example_graph):
        d = dist[node]
        path = reconstruct_path(prev, node)
        if d == float('inf'):
            print(f"  {source} -> {node}: unreachable")
        else:
            print(f"  {source} -> {node}: dist = {d}, path = {path}")
