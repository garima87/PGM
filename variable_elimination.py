import os
import copy

"""
This function find the variable which needs to be eliminated, given the graph and the current factors
"""
def find_var_elim(graph, elimination_nodes, factors):
    min_degree = 10000
    min_filling_edges = 10000
    node = 0
    #Iterate over all the variables that need to be added, and find the one which required adding the minimum number of new edge
    for var in elimination_nodes:
        degree = 0
        filling_edges = 0
        
        #Find factors if we eliminate this variable, and find the number of edges that need to be added in the resulting graph
        new_factors = eliminate_var(factors, var)
        new_graph = copy.deepcopy(graph)
        induced_subgraph, filling_edges = complete_clique(new_graph, new_factors)
       
        if filling_edges < min_filling_edges:
            min_filling_edges = filling_edges
            node = var
    return node

"""
This function finds the factors for a given directed graph
"""
def find_factors(graph):
    factors = []
   
    parent_graph = copy.deepcopy(graph)

    #Change the representation of the graph to point to parents
    for row in xrange(0, len(graph)):
        for col in xrange(0, len(graph[row])):
            if graph[row][col] == 1:   
                parent_graph[col][row] = 1
            else:
                parent_graph[col][row] = 0

    #For each node, add a factor including the node and all its parents
    for row in xrange(0, len(parent_graph)):
        factor = set([row])
        for col in xrange(0, len(parent_graph[row])):
            if parent_graph[row][col] == 0 or row == col: continue
            factor.add(col)
        
        if factor not in factors:
            factors.append(factor)

    return factors

"""
Convert a DAG to an undirected graph
"""
def make_undirected(graph):
    new_graph = graph
    for row in xrange(0, len(graph)):
        for col in xrange(0, len(graph[row])):
            if graph[row][col] == 0 or row == col:  continue
            new_graph[col][row] = 1

"""
Given factors, add edges in the graph to make all the factors cliques in the graph
"""
def complete_clique(graph, factors):
    moralized_graph = copy.deepcopy(graph)
    edges_added = 0
    for factor in factors:
        for node in factor:
            for sibling in factor-set([node]):
                if moralized_graph[node][sibling] == 0: edges_added += 1
                moralized_graph[node][sibling] = 1
                moralized_graph[sibling][node] = 1
            
    return moralized_graph, edges_added

"""
This function computes the new factor, after eliminating a given variable
"""
def eliminate_var(factors, var):
    mod_factors = copy.deepcopy(factors)
    new_factor = set()
    for factor in mod_factors:
        if var in factor:
            factor.remove(var)
            new_factor = new_factor.union(factor)
            mod_factors.remove(factor)
    mod_factors.append(new_factor)
    return mod_factors

"""
The main function, which given a graph and the variables which need to be eliminated, prints the ordering of variable, 
the induced graph and the induced width
"""
def elem_var(graph, variable):
    #Find factors of the initial graph
    factors = find_factors(graph)
    #Remove immoralities in the graph
    moralized_graph, edges = complete_clique(graph, factors)
    induced_subgraph = copy.deepcopy(moralized_graph)
    make_undirected(induced_subgraph)
    var_order = []
    edges = 0
    max_induced_width = max(len(x) for x in factors) - 1

    """
    Iterate till there are some variable which need to be eliminated
    """
    while variable:
        var_elim = find_var_elim(moralized_graph, variable, factors)
        factors = eliminate_var(factors, var_elim)
        induced_subgraph, edges = complete_clique(induced_subgraph, factors)
        induced_width = max(len(x) for x in factors) - 1
        if induced_width > max_induced_width:
            max_induced_width = induced_width
        var_order.append(var_elim)
        variable.remove(var_elim)
 
    print "Variable ordering:", var_order
    print "Induced subgraph:", induced_subgraph
    print "Induced width:", induced_width

    return var_order, induced_subgraph, induced_width

if __name__ == '__main__':
    dag1 = []
    dag1 = [[0 for x in range(12)] for y in range(12)]
    dag1[0][3] = 1
    dag1[1][3] = 1
    dag1[2][4] = 1
    dag1[3][6] = 1
    dag1[3][7] = 1
    dag1[4][7] = 1
    dag1[4][8] = 1
    dag1[5][8] = 1
    dag1[5][9] = 1
    dag1[6][10] = 1
    dag1[7][10] = 1
    dag1[7][11] = 1
    dag1[8][11] = 1
    dag1[8][9] = 1

    elem_var(dag1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11])
    dag2 = []
    dag2 = [[0 for x in range(10)] for y in range(10)]

    dag2[1][3] = 1
    dag2[3][0] = 1
    dag2[3][4] = 1
    dag2[3][6] = 1
    dag2[4][5] = 1
    dag2[4][2] = 1
    dag2[5][7] = 1
    dag2[6][8] = 1
    dag2[7][8] = 1
    dag2[8][9] = 1

    elem_var(dag1, [0, 1, 2, 3, 4, 5, 6, 7, 8])

