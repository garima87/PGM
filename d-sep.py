import os

def find_ancestors(G, E):
    A = E[:]
    G1 = {}
    
    #Change the format of the adjacency to get parents of each node
    for key, value in G.iteritems():
        for item in value:
            if item not in G1:
                G1[item] = []
            l = G1[item]
            l.append(key)
            G1[item] = l
    
    for node in G:
        if node not in G1:
            G1[node] = []
    
    A = E[:]
    new_A = E[:]
    old_A = E[:]
    #Get the set A, of all the ancestors of the evidence variables
    while old_A:
        #Add all the parents of all the nodes which are 
        new_A = []
        for node in old_A:
            if node not in G1:  continue
            parents = G1[node]
            for item in parents:
                if item not in A:
                    new_A.append(item)
                    A.append(item)
        old_A = new_A
    
    return A, G1

def d_separated(G, X, E):
    #Find the ancestors of evidence variable
    A, G1 = find_ancestors(G, E) 

    L = set([(X, 'up')])
    R = set()
    V = set()
    #Apply breadth first search starting from X
    while L:
        v_node = L.pop()
        #Check if the node is visited or not. If it is not, then only we need to visit it. 
        if v_node in V: 
            continue

        node, direc = v_node

        #If the node we are visiting is not an evidence variable, then it can be influenced. Add it to R
        if node not in E:   R.add(node)
        
        #Mark the node visited in that direction
        V.add(v_node)   
        
        #Traverse the node to find all active trails from the node
        if  direc == 'up' and (node not in E):
            parents = G1[node]
            for parent in parents:
                L.add((parent, 'up'))
            
            children = G[node]
            for child in children:
                L.add((child, 'down'))
            
        elif direc == 'down':
            if node not in E:
                children = G[node]
                for child in children:
                    L.add((child, 'down'))     
    
            if node in A:
                parents = G1[node]
                for parent in parents:
                    L.add((parent, 'up'))

    
    ALL = set(G1.keys())
    #The d-seperated nodes are all node minus the nodes that are d-separated
    UR = ALL - R
    return UR

if __name__ == '__main__':
    E = []
    G1 = {}
    G1['A'] = ['D'];
    G1['B'] = ['D'];
    G1['C'] = ['E'];
    G1['D'] = ['G', 'H'];
    G1['E'] = ['I'];
    G1['F'] = ['I', 'J'];
    G1['G'] = ['K'];
    G1['H'] = ['K', 'E'];
    G1['I'] = ['L'];
    G1['J'] = ['M'];
    G1['K'] = [];
    G1['L'] = [];
    G1['M'] = [];
    """
    print "a:", d_separated(G1, 'A', ['K', 'I'])
    print "b:", d_separated(G1, 'G', ['D']) 
    print "c:", d_separated(G1, 'B', ['C', 'L'])
    """
    print "d:", d_separated(G1, 'A', ['K', 'E'])
    print "e:", d_separated(G1, 'B', ['L'])
