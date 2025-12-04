"""
distance_vector.py

A simple synchronous Distance Vector routing simulator.

- Graph is given as adjacency list with link costs.
- Simulates periodic exchange until convergence.
- Optionally supports poisoned reverse in updates.

Usage:
    Run directly: python3 distance_vector.py
"""

from copy import deepcopy
INF = 10**9

def init_tables(nodes, edges):
    """
    nodes: list of node names (strings)
    edges: list of tuples (u, v, cost) - undirected links
    Returns:
      neighbors: dict node -> {neighbor: cost}
      dist: dict node -> dict(dest -> cost)
      next_hop: dict node -> dict(dest -> next_hop)
    """
    neighbors = {u: {} for u in nodes}
    for u, v, c in edges:
        neighbors[u][v] = c
        neighbors[v][u] = c

    dist = {u: {d: INF for d in nodes} for u in nodes}
    next_hop = {u: {d: None for d in nodes} for u in nodes}

    for u in nodes:
        dist[u][u] = 0
        next_hop[u][u] = u
        for v, c in neighbors[u].items():
            dist[u][v] = c
            next_hop[u][v] = v

    return neighbors, dist, next_hop

def send_vector(from_node, to_node, dist_from, use_poisoned_reverse=False):
    """
    Prepare the vector that 'from_node' would send to 'to_node'.
    If poisoned reverse is True, routes whose next_hop is to_node are advertised as INF.
    dist_from: dict(dest->cost) - the sender's current distances
    For our simulator we send full vector (possibly poisoned) as a dict.
    """
    vec = {}
    for dest, cost in dist_from.items():
        if use_poisoned_reverse:
            # If next hop for dest is to_node, poison (advertise INF)
            # NOTE: we don't have next_hop here; caller may implement poison by passing next_hop.
            vec[dest] = cost  # caller will handle poisoning if needed
        else:
            vec[dest] = cost
    return vec

def distance_vector(nodes, edges, use_poisoned_reverse=False, verbose=True):
    neighbors, dist, next_hop = init_tables(nodes, edges)

    # For poisoned reverse we need next_hop info during send; we'll implement poisoning in-loop.
    iteration = 0
    while True:
        iteration += 1
        if verbose:
            print(f"\n=== Iteration {iteration} ===")
        updated = False

        # Make a deep copy of dist to simulate synchronous updates
        old_dist = deepcopy(dist)
        old_next = deepcopy(next_hop)

        # For every node u, we receive vectors from each neighbor v
        for u in nodes:
            for v, cost_uv in neighbors[u].items():
                # Simulate neighbor v sending its current vector to u
                # Build the advertised vector from v to u (with poisoned reverse if enabled)
                advertised = {}
                for dest in nodes:
                    adv_cost = old_dist[v][dest]
                    if use_poisoned_reverse and old_next[v][dest] == u:
                        # v would advertise INF to u for routes that go via u (poisoned reverse)
                        adv_cost = INF
                    advertised[dest] = adv_cost

                # Now u updates its table using the received vector from v
                for dest in nodes:
                    if old_dist[u][v] >= INF:
                        # u cannot reach v according to its old table (shouldn't happen for neighbors),
                        # skip
                        continue
                    via_v = cost_uv + advertised[dest]  # cost u->v + v->dest (advertised)
                    if via_v < dist[u][dest]:
                        dist[u][dest] = via_v
                        next_hop[u][dest] = v
                        updated = True
                        if verbose:
                            print(f"Node {u}: improved route to {dest} via {v} cost {via_v}")

        if not updated:
            if verbose:
                print("\nConverged: no updates in this iteration.")
            break
        if iteration > 50:
            # safety to prevent infinite loop in pathological cases
            if verbose:
                print("Stopping after 50 iterations (safety limit).")
            break

    return dist, next_hop

def pretty_print_tables(nodes, dist, next_hop):
    print("\nRouting tables:")
    for u in nodes:
        print(f"\nNode {u}:")
        print(f"{'Dest':>6} {'Cost':>8} {'NextHop':>8}")
        print("-"*26)
        for dest in nodes:
            c = dist[u][dest]
            nh = next_hop[u][dest]
            cost_str = str(c) if c < INF else "INF"
            nh_str = str(nh) if nh is not None else "-"
            print(f"{dest:>6} {cost_str:>8} {nh_str:>8}")

if __name__ == "__main__":
    # Example network: nodes and undirected edges with costs
    nodes = ["A", "B", "C", "D", "E"]
    edges = [
        ("A","B",1),
        ("A","C",4),
        ("B","C",2),
        ("B","D",7),
        ("C","E",3),
        ("D","E",1)
    ]

    print("Distance Vector Simulator (synchronous rounds)")
    dist, next_hop = distance_vector(nodes, edges, use_poisoned_reverse=True, verbose=True)
    pretty_print_tables(nodes, dist, next_hop)
