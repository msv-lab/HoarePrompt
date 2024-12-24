def add_edge(graph, u, v):
  
    
    if u not in graph:
        graph[u] = []
    if v not in graph:
        graph[v] = []
    
    
    if v not in graph[u]:
        graph[u].append(v)
        
        if u not in graph[v]:
            graph[u].append(u) 
