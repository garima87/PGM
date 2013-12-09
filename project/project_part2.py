import os
import itertools
from numpy import *

class ReadInput:
    def __init__(self,file_name):
       self.filename = file_name
       self._input = []

    def readFile(self):
        fh = open(self.filename, 'r')
        for line in fh:
            _input = [] 
            line = line.strip() 
            values = line.split('\t')
            _input = [int(a) for a in values]
            self._input.append(_input)
        self.array_input = array(self._input)

class GraphPredictor:
    def __init__(self,inputdata, _input):
        self.input_data = inputdata
        self.input_data_t = inputdata.transpose()
        self.nSamples, self.nDim = self.input_data.shape
        self._input = _input
   
    def constructCompleteGraph(self):
        self.dag = {}
        nSamples, nDim = self.input_data.shape
        self.dag = [set(range(0, nDim))-set([x]) for x in range(0, nDim)]
        self.dag = dict(zip(range(len(self.dag)), self.dag))

    def condProb(self, Var, E):
        sum_v = 0.0
        sum_e = 0.0

        for sample in self.input_data:
            cond = True 
            for V, v in E.iteritems():
                if sample[V] != v: 
                    cond = False
                    break
            if cond:
                sum_e += 1
                for V, v in Var.iteritems():
                    if sample[V] != v: 
                        cond = False
                        break
                if cond:
                    sum_v += 1
        
        if sum_e == 0:  return 1
        return (sum_v/sum_e)

    def getAllAssigns(self, evidence_set):
        #print "evidence set is", evidence_set
        evidence_value = [list(x) for x in itertools.product([0, 1], repeat=len(evidence_set))]
        #print "evidence_value is" , evidence_value
        evidence = []
        for evid in evidence_value:
            evidence.append(dict(zip(evidence_set, evid)))
        #print evidence
        return evidence

    def checkIndependence(self, var1, var2, evidence_set):
        #print "Entering check Independence"
        evid_assignments = self.getAllAssigns(evidence_set)
        #print evid_assignments
        sum_entropy = 0.0
        for assign in evid_assignments:
            marginal_prob = self.condProb(assign, {})
            input_val = {}
            summ_x_y = 0.0
            for v1 in 0, 1:
                for v2 in 0, 1:
                    input_val[var1] = v1
                    input_val[var2] = v2
                    combined_prob = self.condProb(input_val, assign) 
                    log_denom = (self.condProb({var1: v1}, assign) * self.condProb({var2: v2}, assign)) 
                    if log_denom == 0:
                        continue
                    log_part = self.condProb(input_val, assign) / log_denom 
                    if log_part == 0:
                        continue
                    summ_x_y += combined_prob * math.log(log_part, 2)
            sum_entropy = sum_entropy + marginal_prob * summ_x_y

        #print "Out of it"
        return sum_entropy < 0.01

    def getCombs(self, adj_var, set_size):
        if set_size > 1:
            return set(itertools.combinations(adj_var, set_size))
        else:
            return [set([x]) for x in adj_var]
            
    def findSkeleton(self, max_links):
        self.constructCompleteGraph()
        indep_evidence = {}
        set_size = 1 
                   
        for var1 in range(0, self.nDim-1):
            for var2 in range(var1+1, self.nDim):
                if self.checkIndependence(var1, var2, set()):
                    self.dag[var1].remove(var2)
                    self.dag[var2].remove(var1)
                
        print self.dag
        for var1 in range(0, self.nDim-1):
            for var2 in range(var1+1, self.nDim):
            #for var2 in self.dag[var1]:
                if var2 not in self.dag[var1]:
                    continue
                #print var1, var2
                set_size = 1
                independent = False
                adj_vars = self.dag[var1] - set([var2]) 
                while (not independent) and (set_size <= max_links):
                    possible_sets = self.getCombs(adj_vars, set_size)
                    #print possible_sets
                    for e_set in possible_sets:
                        #print e_set
                        if self.checkIndependence(var1, var2, e_set):
                            #print "Removing edge", var1, var2
                            #print "Evidence is", e_set
                            indep_evidence[str(var1) + str(var2)] = e_set
                            independent = True
                            self.dag[var1].remove(var2)
                            self.dag[var2].remove(var1)
                            break
                    set_size += 1
        print self.dag

if __name__ == '__main__':
    inputObj = ReadInput("train1000.txt")
    inputObj.readFile()
    graphObj = GraphPredictor(inputObj.array_input, inputObj._input)
    graphObj.findSkeleton(4)
