"""
src/prescription/structural/structural_metrics.py

Pure Python implementations of structural graph metrics (degree, centrality, density).
Designed to avoid external dependencies like NetworkX for small prescription networks (V <= 20).
"""

from typing import List, Dict, Tuple, Set
from collections import deque

def calculate_degrees(nodes: List[str], edges: List[Tuple[str, str, float]]) -> Tuple[Dict[str, int], Dict[str, float]]:
    """
    Calculates degree and weighted degree for each node.
    - nodes: List of node IDs.
    - edges: List of tuples (node_a, node_b, edge_strength).
    
    Returns:
        Tuple[degree_dict, weighted_degree_dict]
    """
    degrees = {n: 0 for n in nodes}
    weighted_degrees = {n: 0.0 for n in nodes}
    
    for u, v, strength in edges:
        if u in degrees:
            degrees[u] += 1
            weighted_degrees[u] += strength
        if v in degrees:
            degrees[v] += 1
            weighted_degrees[v] += strength
            
    return degrees, weighted_degrees

def calculate_betweenness_centrality(nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, float]:
    """
    Calculates normalized betweenness centrality for an undirected graph using Brandes' algorithm.
    - nodes: List of node IDs.
    - edges: List of tuples (node_a, node_b).
    """
    adj = {n: [] for n in nodes}
    for u, v in edges:
        if u in adj and v in adj:
            adj[u].append(v)
            adj[v].append(u)
            
    betweenness = {n: 0.0 for n in nodes}
    
    for s in nodes:
        # Step 1: Single-source shortest paths using BFS
        S = []
        P = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        sigma[s] = 1
        d = {w: -1 for w in nodes}
        d[s] = 0
        
        Q = deque([s])
        while Q:
            v = Q.popleft()
            S.append(v)
            for w in adj[v]:
                # Path discovery
                if d[w] < 0:
                    d[w] = d[v] + 1
                    Q.append(w)
                # Path counting
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)
                    
        # Step 2: Accumulate dependency back propagation
        delta = {w: 0.0 for w in nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                betweenness[w] += delta[w]
                
    # Step 3: Scale down because graph is undirected
    for n in betweenness:
        betweenness[n] /= 2.0
        
    # Step 4: Normalize by dividing by maximum possible pairs excluding the node
    N = len(nodes)
    if N > 2:
        scale = (N - 1) * (N - 2) / 2.0
        for n in betweenness:
            betweenness[n] /= scale
    else:
        for n in betweenness:
            betweenness[n] = 0.0
            
    return betweenness

def calculate_density(num_nodes: int, num_edges: int) -> float:
    """
    Calculates the density of a cluster or graph.
    Density = E / (V * (V - 1) / 2)
    """
    if num_nodes <= 1:
        return 0.0
    possible_edges = (num_nodes * (num_nodes - 1)) / 2.0
    return float(num_edges) / possible_edges
