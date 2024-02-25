import pyAgrum as gum
import re
from deepdiff import DeepDiff


# this class models a component in the system
# the component is defined by it's name and specs (a dict)
# from the specs the internal variables are determined
class Component:
    def __init__(self, name, specs):
        self.name = name                                       # name of the component
        self.specs = specs                                     # dict specifying component
        self.variables = []                                    # Labelized variables used to generate nodes in diagram
        self.internalconnections = []                          # arcs between inputs > output + healt > output
        self.cptoutput = gum.Potential()                       # specification of cpt for outputnode
        self.setVariables()                           
        self.setInternalConnections()
        self.setCptOutput()

    # create pyAgrum Labelized variables per node in the component
    # private method
    def setVariables(self):
        v = self.specs["Outputs"]["1"]
        varname = str( v['property'] + v['modality']+ "Outputs" + self.name)
        self.variables.append(gum.LabelizedVariable(varname, varname, v['propertyvalues'])) 
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs" + self.name)
            self.variables.append(gum.LabelizedVariable(varname, varname, v['propertyvalues']))            
        v = self.specs["Healths"]["1"]
        varname = str(v["property"] + self.name)
        self.variables.append(gum.LabelizedVariable(varname, varname, v['propertyvalues']))

    # define the connections that are internal to the component
    # private method
    def setInternalConnections(self):
        # define connections for inputs / health nodes to output within component
        for variable in self.variables:
            if(re.search("Outputs", variable.name())):
                outputname = variable.name()
        for variable in self.variables:
            if(re.search("Inputs", variable.name())):
                self.internalconnections.append((variable.name(), outputname))
            elif(re.search("health", variable.name())):
                self.internalconnections.append((variable.name(), outputname))
    

    # transforms the readable behavior table from specs to a format for use
    # during creation of a potential
    def transformBehaviorTable(self):
        cptDict = {}
        for k, v in self.specs['Behavior']['normal'].items():
            var = k + self.getName()
            count = 0
            for e in v:
                if count in cptDict:
                    d = cptDict[count]
                    d[var] = e
                else:
                    cptDict[count] = {var: e}
                count = count + 1
        return cptDict


    # read the normal behavior table, transform to potential 
    # private method
    def setCptOutput(self):
        # first create the potential with all the probabilities
        # P(X | Y, Z) X should be first variable when creating potential
        x = None
        yz = []

        # number of labels for X is relevant for determinining probability later on
        xnumberoflabels = None

        for l in self.getVariables():
            if "Output" in l.name():
                x = l
                xnumberoflabels = len(l.labels())
            else:
                yz.append(l)

        p = gum.Potential().add(x)
        for y in yz:
            p.add(y)

        # second fill potential based on values from behavior table 
        behavior = self.transformBehaviorTable()

        for potentialindex in p.loopIn():
            pid = potentialindex.todict()
            for k, v in behavior.items():
                if ('values_changed' not in DeepDiff(pid, v).keys()):
                    prob = 1 - ((xnumberoflabels - 1) * 0.01)
                    p.set(potentialindex, prob)
                    break
                else:
                    p.set(potentialindex, 0.01)

        self.cptoutput = p



# get methods
# public methods                
    def getComponentNodeNames(self):
        varlist = []
        for var in self.variables:
            varlist.append(var.name())
        return varlist

    # name of component as string
    def getName(self):
        return self.name

    # variables for component as pyAgrum  list of variables
    def getVariables(self):
        return self.variables

    # get internal connections to component as list of tuples
    def getInternalConnections(self):
        return self.internalconnections
    
    # get conditional probability table for output node as dict
    def getCptOutput(self):
        return self.cptoutput
    
    # get name as string
    def getHealthVarName(self):
        for name in self.getComponentNodeNames():
            if (re.search("health", name)):
                return name

    # get prior as list of probabilities
    def getHealthPrior(self):
        v = self.specs["Healths"]["1"]
        return v["priorprobability"]
    
    def getOutputsVarName(self):
        for name in self.getComponentNodeNames():
            if (re.search("Outputs", name)):
                return name
    def getInputsVarNames(self):
        nodenames = []
        for name in self.getComponentNodeNames():
            if (re.search("Inputs", name)):
                nodenames.append(name)
        return nodenames
    def getInputPrior(self, inputitem):
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs" + self.name)
            if (varname == inputitem):
                return v["priorprobability"]
    







# class Connection models connections between component in the system
# a connection is defined by it's name, specs (dict) and start + end components

class Connection:
    def __init__(self, name, specs, startnode, endnode):
        self.name = name                                     # name of the connection
        self.specs = specs                                   # dict specifying properties of connection
        self.startnode = startnode                           # name of variable starting point for connection
        self.endnode = endnode                               # name of variable ending point for connection
        self.cptendcomponent = None
        self.setCptEndComponent()                            # potentional for cpt
        
    # create pyAgrum labelized variable used when adding health for connection to diagram
    def getHealthVariable(self):
        label = "health" + self.name
        v = self.specs["Healths"]["1"]
        propertyvalues = v["propertyvalues"]
        return gum.LabelizedVariable(label, label, propertyvalues)
    
    # determine start / end component names
    def addComponentName(self, name):
        if (re.search(name, self.startnode)): return self.startnode
        elif (re.search(name, self.endnode)): return self.endnode
        elif (re.search("health", name)): return name + self.name
        
    # determine cpt for connection
    # connection consists of startnode, endnode and healthnode
    # endnode is a input node, startnode is a outputnode
    def setCptEndComponent(self):
        # transform behavior table
        cptDict = {}
        for k, v in self.specs['Behavior']['normal'].items():
            var = k + self.addComponentName(k)
            count = 0
            for e in v:
                if count in cptDict:
                    d = cptDict[count]
                    d[var] = e
                else:
                    cptDict[count] = {var: e}
                count = count + 1
        return cptDict


        

    # get methods
    def getStartNode(self):
        return self.startnode
    def getEndNode(self):
        return self.endnode
    def getCptEndComponent(self):
        return self.cptendcomponent
    def getHealthPrior(self):
        v = self.specs["Healths"]["1"]
        return v["priorprobability"]
    def getName(self):
        return self.name
    




# class test models an observation test
# test is defined by it's name, the target component (healthnode) and a dict containing specs

class ObserveTest:
    def __init__(self, name, target, specs):
        self.name = name
        self.target = target
        self.specs = specs
        self.decisionvalues = self.specs["decisionvalues"]
        self.testoutcomevalues = self.specs["testoutcomevalues"]
        self.testcosts = self.specs["testcosts"]
        self.testoutcomecpt = {}
        self.setCptTestOutcomeNode()
        self.testoutcometargetnode = self.setTestOutcomeToReplaceDecision()
        
    def setTestOutcomeToReplaceDecision(self):
        if(self.specs["testoutcomeToReplaceDecision"] == True):
            return str("DecisionReplace" + self.target)
        else: 
            return None
    def addComponentName(self, x):
        return x + self.target
    def setCptTestOutcomeNode(self):
        cptDict = {}
        for k, v in self.specs['testoutcomecpt'].items():
            var = k + self.addComponentName(k)
            count = 0
            for e in v:
                if count in cptDict:
                    d = cptDict[count]
                    d[var] = e
                else:
                    cptDict[count] = {var: e}
                count = count + 1
        self.testoutcomecpt = cptDict
    def getTestOutcomeCpt(self):
        return self.testoutcomecpt     
    def getName(self):
        return self.name
    def getTarget(self):
        return self.target
    def getDecisionValues(self):
        return self.decisionvalues 
    def getTestOutcomeValues(self):
        return self.testoutcomevalues
    def getTestCosts(self):
        return self.testcosts
    def getTestoutcometargetNode(self):
        return self.testoutcometargetnode
    





# class assembly contains objects for all part of the system: components, connections, tests

class Assembly:
    def __init__(self, name, components, connections, tests):
        self.name = name
        self.components = components
        self.connections = connections
        self.tests = tests
    def getName(self):
        return self.name
    def getComponents(self):
        return self.components
    def getConnections(self):
        return self.connections
    def getTests(self):
        return self.tests
    
