import pyAgrum as gum
import re
from deepdiff import DeepDiff



class Node:
    def __init__(self, name, nodetype, variable):
        self.name = name
        self.type = nodetype
        self.variable = variable                      # pyAgrum LabelizedVariable
        self.prior = None                             # pyAgrum Potential

    def setPrior(self, prior):
        self.prior = prior
    
    def getPrior(self):
        return self.prior

    def getName(self):
        return self.name
    
    def getType(self):
        return self.type
    
    def getVariable(self):
        return self.variable




# this class models a component in the system
# the component is defined by it's name and specs (a dict)
# from the specs the internal variables are determined
class Component:
    def __init__(self, name, specs):
        self.name = name                                       # name of the component
        self.specs = specs                                     # dict specifying component
        self.nodes = []
        self.internalconnections = []                          # internal arcs, list of tuples
        self.createNodes()
        self.setInternalConnections()
        self.setPriorOutput()
        self.setPriorHealth()
        self.setPriorInputs()


    def createNodes(self):
        # create outputnode
        v = self.specs["Outputs"]["1"]
        varname = str( v['property'] + v['modality']+ "Outputs" + self.name)
        node = Node(varname, "Output", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
        self.nodes.append(node)

        # create input nodes
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs" + self.name)
            node = Node(varname, "Input", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
            self.nodes.append(node)
        # create health node
        v = self.specs["Healths"]["1"]
        varname = str(v["property"] + self.name)
        node = Node(varname, "Health", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
        self.nodes.append(node)
        

    # define the connections that are internal to the component
    # private method
    def setInternalConnections(self):
        # define connections for inputs / health nodes to output within component
        for variable in self.getNodeVariables():
            if(re.search("Outputs", variable.name())):
                outputname = variable.name()
        for variable in self.getNodeVariables():
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
    def setPriorOutput(self):
        # first create the potential with all the probabilities
        # P(X | Y, Z) X should be first variable when creating potential
        x = None
        yz = []

        # number of labels for X is relevant for determinining probability later on
        xnumberoflabels = None

        for l in self.getNodeVariables():
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

        # add potential to node
        for node in self.getNodes():
            if (node.getType() == "Output"):
                node.setPrior(p)


    # set the prior of the health node
    # assumption is health has states ok / broken and specs contains [0.99, 0.01]
    def setPriorHealth(self):
        # get prior from spec, health has no parents
        p = self.specs["Healths"]["1"]["priorprobability"]
        hnode = self.getHealthNode()
        hnode.setPrior(self.generateInstantiationTuples([hnode.getVariable()], p))


    def findInputPriorFromSpecs(self, inputname):
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs" + self.name)
            if (varname == inputname):
                return v["priorprobability"]



    def setPriorInputs(self):
        for node in self.getInputNodes():
            p = self.findInputPriorFromSpecs(node.getName())
            node.setPrior(self.generateInstantiationTuples([node.getVariable()], p))

                                           
    def generateInstantiationTuples(self, vars, priors):
        pot = gum.Potential()
        i = gum.Instantiation()
        for v in vars:
            pot.add(v)
            i.add(v)
        for p in priors:
            pot.set(i, p)
            if i.end():
                break
            else:
                i.inc()
        return pot



# get methods
# public methods                
    def getComponentNodeNames(self):
        nodenames = []
        for node in self.nodes:
            nodenames.append(node.getName())
        return nodenames

    # name of component as string
    def getName(self):
        return self.name

    # variables for component as pyAgrum  list of variables
    def getNodeVariables(self):
        nodevariables = []
        for node in self.nodes:
            nodevariables.append(node.getVariable())
        return nodevariables
    
    # nodes of component
    def getNodes(self):
        return  self.nodes

    # get internal connections to component as list of tuples
    def getInternalConnections(self):
        return self.internalconnections
    
    def getHealthNode(self):
        for node in self.getNodes():
            if (node.getType() == "Health"):
                return node

    # get name as string
    def getHealthVarName(self):
        for node in self.getNodes():
            if (node.getType() == "Health"):
                return node.getName()
    
    def getOutputNode(self):
        for node in self.getNodes():
            if (node.getType() == "Output"):
                return node

    def getOutputsVarName(self):
        for node in self.getNodes():
            if (node.getType() == "Output"):
                return node.getName()

    def getInputNodes(self):
        nodes = []
        for node in self.getNodes():
            if (node.getType() == "Input"):
                nodes.append(node)
        return nodes

    def getInputsVarNames(self):
        nodenames = []
        for node in self.getInputNodes():
            nodenames.append(node.getName())
        return nodenames

    # get prior as list of probabilities
    def getHealthPrior(self):
        return self.getHealthNode().getPrior()


    def getInputPrior(self, inputitem):
        for node in self.getInputNodes():
            if (node.getName() == "inputitem"):
                return node.getPrior()
    







# class Connection models connections between component in the system
# a connection is defined by it's name, specs (dict) and start + end components

class Connection:
    def __init__(self, name, specs, startcomponent, endcomponent):
        self.name = name                                     # name of the connection
        self.specs = specs                                   # dict specifying properties of connection
        self.startcomponent = startcomponent
        self.endcomponent = endcomponent
        self.startnode = None                                # node that is starting point for connection
        self.endnode = None                                  # node that is ending point for connection
        self.healthnode = None
        self.cptendcomponent = None
        self.setHealthVariable()
        self.setPriorHealth()
        self.setStartEndNodes()
        self.setCptEndNode()                                 # potentional for cpt

        
    # create pyAgrum labelized variable used when adding health for connection to diagram
    def setHealthVariable(self):
        label = "health" + self.name
        v = self.specs["Healths"]["1"]
        self.healthnode = Node(label, "Health", gum.LabelizedVariable(label, label, v['propertyvalues']))

    # set the prior of the health node
    # assumption is health has states ok / broken and specs contains [0.99, 0.01]
    def setPriorHealth(self):
        # get prior from spec, health has no parents
        p = self.specs["Healths"]["1"]["priorprobability"]
        self.healthnode.setPrior(self.generateInstantiationTuples([self.healthnode.getVariable()], p))

    def generateInstantiationTuples(self, vars, priors):
        pot = gum.Potential()
        i = gum.Instantiation()
        for v in vars:
            pot.add(v)
            i.add(v)
        for p in priors:
            pot.set(i, p)
            if i.end():
                break
            else:
                i.inc()
        return pot



    def setStartEndNodes(self):
        startnodename = str(self.specs['start'] + self.startcomponent.getName())
        for node in self.startcomponent.getNodes():
            if (node.getName() == startnodename): self.startnode = node
            break

        endnodename = str(self.specs['end'] + self.endcomponent.getName())
        for node in self.endcomponent.getNodes():
            if (node.getName() == endnodename): self.endnode = node

    


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


    def setCptEndNode(self):
        # first extend potential
        potential = self.endnode.getPrior()
        labelvar = self.startnode.getVariable()
        potential.add(labelvar)
        
        # second fill potential based on values from behavior table 
        behavior = self.transformBehaviorTable()

        xnumberoflabels = len(self.endnode.getVariable().labels())

        for potentialindex in potential.loopIn():
            pid = potentialindex.todict()
            for k, v in behavior.items():
                if ('values_changed' not in DeepDiff(pid, v).keys()):
                    prob = 1 - ((xnumberoflabels - 1) * 0.01)
                    potential.set(potentialindex, prob)
                    break
                else:
                    potential.set(potentialindex, 0.01)

        # add potential to node
        self.endnode.setPrior(potential)




    # get methods
    def getName(self):
        return self.name
    def getStartNode(self):
        return self.startnode
    def getEndNode(self):
        return self.endnode    
    




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
    
