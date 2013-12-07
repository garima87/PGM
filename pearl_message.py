"""
Author - Garima Agarwal
Date - 12/01/2013
Description - Function to implement Pearl's Message Passing Algorithm
"""

import os
import copy

#Global variables 
#E is the set of evidence variable which we have seen so far
E = set()
#e is the set of value of evidence variable which we have seen so far
e = set()

#lambdaNode stores the lambda value of a particular node. It is a 2D list.
lambdaNode = {}
#_lambda is the message passed from the child node to the parent node. It is a 3D list 
_lambda = {}
#pi stores the pi value for a node. It is a 2D list
pi = {}
#piNode stores the messages passed from parent to child node.
piNode = {}
#the graph store in a transformed format to point to parent instead of children
parentDAG = {}
#original graph
originalDAG = {}
#Probability of a variable, given evidence
prob_evid = {}
#The probability for a given graph, which is the input
prob = {}

def get_parent_graph(DAG):
    #Change the format of the adjacency to get parents of each node
    parentDAG = {}
    for key, value in DAG.iteritems():
        for item in value:
            if item not in parentDAG:
                parentDAG[item] = []
            l = parentDAG[item]
            l.append(key)
            parentDAG[item] = l
    
    for node in DAG:
        if node not in parentDAG:
            parentDAG[node] = []

    return parentDAG
    

def initialize_network(nodes, DAG, roots):
    #This function initializes the network. It should be called each time we want to calculate probability given some evidence
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid, prob
    E = set()
    e = set()
    lambdaNode = {}
    _lambda = {}
    pi = {}
    piNode = {}
    prob_evid = {}

    parentDAG = get_parent_graph(DAG)
    originalDAG = DAG
    #initialize the lambda and pie values
    for node in nodes:
        lambdaNode[node] = {}
        for value in val(node):
            lambdaNode[node][value] = 1

        _lambda[node] = {}
        
        for parent in parentDAG[node]:
            _lambda[node][parent] = {}
            for value in val(parent):
                _lambda[node][parent][value] = 1    

        for child in DAG[node]:
            if child not in pi:
                pi[child] = {}
            pi[child][node] = {}
            for value in val(child):
                pi[child][node][value] = 1    
    
    #For the root elements, set the pi values and probability given evidence to be the given probabilities
    for root in roots:
        if root not in piNode:
            piNode[root] = {} 
        prob_evid[root] = {}
        for value in val(root):
           piNode[root][value] = prob[str(root) + str(value)]
           prob_evid[root][value] = prob[str(root) + str(value)] 

        for child in DAG[root]:
            #propogate pi message to all the children
            send_pi_message(root, child);

#Update function to update the network with evidence variables
def update_network(variable, value):
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid
    E = E.union(set([variable]))
    e = e.union(set([value]))

    #For the evidence variable, set lambda and pi values to reflect the value of the variable
    for v in val(variable):
        if(v == value):
            lambdaNode[variable][v] = 1.0
            piNode[variable][v] = 1.0
            prob_evid[variable][v] = 1.0
        else:
            lambdaNode[variable][v] = 0.0
            piNode[variable][v] = 0.0
            prob_evid[variable][v] = 0.0


    #Send lambda message to all the parents which are not in evidence set
    for parent in parentDAG[variable]:
        if parent in E: 
            continue

        send_lambda_message(variable, parent)

    #Pass pi message to all the children
    for child in originalDAG[variable]:
        send_pi_message(variable, child)

#function which returns the valid values for a particular variable. In our case all variables are binary, so the valid values are 0, 1
def val(X):
    return [0, 1]

#function to find all the possible assignments to parent variables
def find_all_combs(assign, parents, index, Y, y):
    global prob
    if index == len(parents):
        assign_sort = sorted(assign)
        result = ''.join(assign_sort)
        prob_r = prob[str(Y) + str(y)][result] 
        for parent in assign[1:]:
            #print "Value of pi is:", pi
            #print parent[0], Y, parent[1]
            prob_r = prob_r * pi[Y][parent[0]][int(parent[1])]
        return prob_r
   
    prob_r = 0
    possibleAssign = str(parents[index]) + str(0)
    assign1 = copy.deepcopy(assign)
    assign2 = copy.deepcopy(assign)
    assign1.append(possibleAssign)
    prob_r += find_all_combs(assign1, parents, index+1, Y, y)
    possibleAssign = str(parents[index]) + str(1)
    assign2.append(possibleAssign)
    prob_r += find_all_combs(assign2, parents, index+1, Y, y)
    return prob_r
    

#function to marginalize 
def marginalize(Y, y, X, x):
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid

    parents = []
    for parent in parentDAG[Y]:
        if parent == X:
            continue
        parents.append(parent)

    assign = [str(X) + str(x)]
    marginalized_prob = 0
    marginalized_prob = find_all_combs(assign, parents, 0, Y, y)
    return marginalized_prob 

#function to send lambda message from Y(child) -> X(parent)
def send_lambda_message(Y, X):
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid

    pTilde = {}
    for value in val(X):
        _lambda[Y][X][value] = 0
        for valuep in val(Y):
            _lambda[Y][X][value] += marginalize(Y, valuep, X, value) * lambdaNode[Y][valuep]

        lambdaNode[X][value] = 1    
        for child in originalDAG[X]:
            lambdaNode[X][value] = lambdaNode[X][value] * _lambda[child][X][value]

        pTilde[value] = lambdaNode[X][value] * piNode[X][value]

    alpha = sum(pTilde.values())
   
    if X not in prob_evid:
        prob_evid[X] = {}

    for value in val(X):
        prob_evid[X][value] = (float)(pTilde[value]) / alpha

    for parent in parentDAG[X]:
        if parent in E:
            continue

        send_lambda_message(X, parent)

    for child in (set(originalDAG[X]) - set([Y])):
        send_pi_message(X, child)


#function to find all the possible assignments to parent variables
def find_all_combs_pi(assign, parents, index, Y, y):
    if index == len(parents):
        assign_sort = sorted(assign)
        result = ''.join(assign_sort)
        prob_r = prob[str(Y) + str(y)][result]
        for parent in assign:
            prob_r = prob_r * pi[Y][parent[0]][int(parent[1])]
        return prob_r 
    
    prob_r = 0
    possibleAssign = str(parents[index]) + str(0)
    assign1 = copy.deepcopy(assign)
    assign2 = copy.deepcopy(assign)
    assign1.append(possibleAssign)
    prob_r += find_all_combs_pi(assign1, parents, index+1, Y, y)
    possibleAssign = str(parents[index]) + str(1)
    assign2.append(possibleAssign)
    prob_r += find_all_combs_pi(assign2, parents, index+1, Y, y)
    return prob_r
    
#Marginalization used in send_pi_message function
def marginalize_pi(X, x):
    assign = []
    return_value = 0
    return_value = find_all_combs_pi(assign, parentDAG[X], 0, X, x)
    #print "return value is", return_value
    return return_value


def check_lambda(X):
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid

    for value in lambdaNode[X]:
		if lambdaNode[X][value] != 1.0: 
			return True
    
    return False

#function to send pi  message from Z(parent) -> X(child)
def send_pi_message(Z, X): 
    #print "Sending pi message from ", Z, "to", X
    global E, e, lambdaNode, _lambda, pi, parentDAG, originalDAG, piNode, prob_evid

    for z in val(Z):
        #print "Value of pi is:", pi[X], X, Z
        pi[X][Z][z] = piNode[Z][z]
        for child in originalDAG[Z]:
            if child == X:
                continue
            pi[X][Z][z] = pi[X][Z][z] * _lambda[child][Z][z]

    pTilde = {}
    if X not in piNode:
        piNode[X] = {}

    if X not in E:
        #check this
        for x in val(X):
            piNode[X][x] = marginalize_pi(X, x)
            pTilde[x] = piNode[X][x] * lambdaNode[X][x]
    

        alpha = sum(pTilde.values())
        if X not in prob_evid:
            prob_evid[X] = {}
   
        for x in val(X):
            prob_evid[X][x] = (float)(pTilde[x]) / alpha

        for child in originalDAG[X]:
            send_pi_message(X, child)

    #If there exists a lambda message which is not 1, propogate lambda messages
    if check_lambda(X):
        for parent in parentDAG[X]:
            if parent == Z:
                continue
            if parent in E:
                continue
            send_lambda_message(X, parent)

def get_prob():
    global prob
    prob['A1'] = 0.7
    prob['A0'] = 0.3
    prob['B1'] = 0.4
    prob['B0'] = 0.6
    prob['C1'] = {}
    prob['C0'] = {}
    prob['C1']['A0B0'] = 0.1
    prob['C1']['A0B1'] = 0.5
    prob['C1']['A1B0'] = 0.3
    prob['C1']['A1B1'] = 0.9
    prob['C0']['A0B0'] = 0.9
    prob['C0']['A0B1'] = 0.5
    prob['C0']['A1B0'] = 0.7
    prob['C0']['A1B1'] = 0.1

    prob['D1'] = {}
    prob['D0'] = {}
    prob['D1']['C0'] = 0.8
    prob['D1']['C1'] = 0.3
    prob['D0']['C0'] = 0.2
    prob['D0']['C1'] = 0.7
    
    prob['E1'] = {}
    prob['E0'] = {}
    prob['E1']['C0'] = 0.2 
    prob['E1']['C1'] = 0.6
    prob['E0']['C0'] = 0.8
    prob['E0']['C1'] = 0.4

    prob['F1'] = {}
    prob['F0'] = {}
    prob['F1']['D0'] = 0.1
    prob['F1']['D1'] = 0.7
    prob['F0']['D0'] = 0.9
    prob['F0']['D1'] = 0.3

    prob['G1'] = {}
    prob['G0'] = {}
    prob['G1']['D0'] = 0.9
    prob['G1']['D1'] = 0.4
    prob['G0']['D0'] = 0.1
    prob['G0']['D1'] = 0.6
    return prob



def get_final_probs(DAG, roots, nodes, evidence, observe):    
    initialize_network(nodes, DAG, roots)
    print "Evidence:", evidence 
    print "Values to observe", observe
    for variable, value in evidence.iteritems():
        update_network(variable, value)


    prob = 1.0
    for variable, value in observe.iteritems():
        prob = prob * prob_evid[variable][value]
        update_network(variable, value)

    print "Prob is:", prob
    print

if __name__ == '__main__':
    DAG = {}
    DAG['A'] = ['C']
    DAG['B'] = ['C']
    DAG['C'] = ['D', 'E']
    DAG['D'] = ['F', 'G']
    DAG['E'] = []
    DAG['F'] = []
    DAG['G'] = []
    
    nodes = DAG.keys()
    prob = get_prob()
    roots = ['A', 'B']
    
    #Find the prob of A=1, given evidence
    evidence = {'B':0}
    observe = {'A':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0, 'B':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0, 'G':1}
    
    #Find the prob for B=1, given evidence
    observe = {'B':1}
    evidence = {'A':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1, 'C':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    
    #Find the prob of C=1, given evidence
    observe = {'C':1}
    evidence = {}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1, 'B':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0, 'F':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
     
    #Find the prob of D=1, given evidence
    observe = {'D':1}
    evidence = {}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'E':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':0, 'E':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'B':1, 'G':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'B':1, 'G':0, 'F':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)

    #Find the prob of E=1, given evidence
    observe = {'E':1}
    evidence = {}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'F':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':1, 'F':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1, 'B':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    
    #Find the prob of F=1, given evidence
    observe = {'F':1}
    evidence = {}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1, 'C':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'A':1, 'C':0, 'E':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'B':1, 'G':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)

    #Find the prob of G=1, given evidence
    observe = {'G':1}
    evidence = {}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'C':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'D':0, 'C':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'E':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    evidence = {'B':1, 'A':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)


    observe = {'A':1, 'D':1}
    evidence = {'F':0, 'B':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)

    observe = {'C':0, 'E':1}
    evidence = {'F':1, 'G':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)

    observe = {'F':0, 'B':1}
    evidence = {'G':0, 'E':1}
    get_final_probs(DAG, roots, nodes, evidence, observe)
    
    observe = {'G':1, 'B':0}
    evidence = {'F':1, 'A':0}
    get_final_probs(DAG, roots, nodes, evidence, observe)
