import pyAgrum as gum
import re
#import pandas as pd


# this class models a component in the system
# the component is defined by it's name and specs (a dict)
# from the specs the internal variables are determined
class Component:
    def __init__(self, name, specs):
        self.name = name                                       # name of the component
        self.specs = specs                                     # dict specifying component
        self.variables = []                                    # Labelized variables used to generate nodes in diagram
        self.internalconnections = []                          # arcs between inputs > output + healt > output
        self.cptoutput = {}                                    # specification of cpt for outputnode
        self.replacedecision = {}                              # dict specifying nodes necessary to model replace decision
        self.setVariables()                           
        self.setInternalConnections()
        self.setCptOutput()
        self.setReplaceDecision()

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
    
    # read the normal behavior table, store in format that can be used later
    # private method
    def setCptOutput(self):
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
        self.cptoutput = cptDict




    # create dict with specification of a replace decision
    # private method
    def setReplaceDecision(self):
        for k, decision in self.specs["Decisions"].items():
            if (re.search("Replace", decision["name"])):
                decisionvarname = "Decision" + decision["name"] + self.name
                utilityvarname = "Utility" + decision["name"] + self.name
                self.replacedecision["decision"] = gum.LabelizedVariable(decisionvarname, decisionvarname, decision['values'])
                self.replacedecision["utility"] = gum.LabelizedVariable(utilityvarname, utilityvarname, 1)
                self.replacedecision["arcs"] = [(decisionvarname, utilityvarname),(self.getHealthVarName(), utilityvarname)]
                self.replacedecision["replacementcosts"] = decision["replacementcosts"]
                self.replacedecision["incorrectreplacementcosts"] = decision["incorrectreplacementcosts"]
                self.replacedecision["failuretorepaircosts"] = decision["failuretorepaircosts"]


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
    def getReplaceDecision(self):
        return self.replacedecision
    







# class Connection models connections between component in the system
# a connection is defined by it's name, specs (dict) and start + end components

class Connection:
    def __init__(self, name, specs, startnode, endnode):
        self.name = name                                     # name of the connection
        self.specs = specs                                   # dict specifying properties of connection
        self.startnode = startnode                           # name of variable starting point for connection
        self.endnode = endnode                               # name of variable ending point for connection
        self.cptendcomponent = self.setCptEndComponent()     # storing normal behavior table
        
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
        
    # prepare normal behavior table for later use determining cpt of endcomponent
    def setCptEndComponent(self):
        dfstates = pd.DataFrame.from_dict(data = self.specs['Behavior']['normal'])
        dfstates.rename(columns=lambda x: self.addComponentName(x), inplace=True)
        # transform dataframe back to dict but in different format for comparison
        return dfstates.to_dict('index')

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
        dfstates = pd.DataFrame.from_dict(data = self.specs["testoutcomecpt"])
        dfstates.rename(columns=lambda x: self.addComponentName(x), inplace=True)
        self.testoutcomecpt =  dfstates.to_dict("index")
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
    def getComponents(self):
        return self.components
    def getConnections(self):
        return self.connections
    def getTests(self):
        return self.tests
    














# helper to find a specification that matches a given type
def getTypeSpecs(specs, ctype):
    for c in specs:
        if (c["type"] == ctype):
            return c

# helper to find a specific component by name in list of components
def findComponent(requestedcomponent, componentlist):
    for component in componentlist:
        if (component.getName() == requestedcomponent):
            return component

# helper to determine start / end nodes based on list of existing components and connection specs
def determineConnectionStartEndNodes(connection, componentslist, specs):
    # determine startComponent: variablename
    startcomponentobject = findComponent(connection["startComponent"], componentslist)
    endcomponentobject = findComponent(connection["endComponent"], componentslist)
    for label in startcomponentobject.getVariables():
        if(re.search(specs["start"], label.name())):
            startname = label.name()
    for label in endcomponentobject.getVariables():
        if(re.search(specs["end"], label.name())):
            endname = label.name()
    return (startname, endname)

    
# create components objects
# loop structure, find specs, create component object
def getComponents(assembly):
    componentObjects = []
    for k, component in assembly["structure"]["components"].items():
        specs = getTypeSpecs(assembly["components"], component['type'])
        componentObjects.append(Component(component["name"], specs))
    return componentObjects
    

# create connections objects
# loop connections in structure, find specs and start/end components,  create connection object
def getConnections(assembly, componentslist):
    connectionObjects = []
    try:
        for k, conn in assembly["structure"]["connections"].items():
            specs = getTypeSpecs(assembly["connections"], conn["type"])
            startendnames = determineConnectionStartEndNodes(conn, componentslist, specs)
            connectionObjects.append(Connection(conn["name"], specs,startendnames[0],startendnames[1]))
    except KeyError:
        print("KeyError, no connections found")
    return connectionObjects


# create Test objects
# loop the testmapping specification, find test specs + targetnode, create testobject
def getTests(assembly, componentslist):
    testObjects = []
    for k, test in assembly['testmapping'].items():
        for testtype in assembly["tests"]:
            if (test["test"] == testtype["name"]):
                specs = testtype
                testObjects.append(Test(testtype['name'], test["target"], specs))
    return testObjects
        
    
# MAIN method to build objects and create a system definition
def createSystemFromSpecs(assembly):
    name = assembly['structure']["name"]
    print("building system: " + name)

    componentslist = getComponents(assembly)
    print("number of components: " + str(len(componentslist)))

    connectionslist = getConnections(assembly, componentslist)
    print("number of connections: " + str(len(connectionslist)))

    testslist = getTests(assembly, componentslist)
    print("number of tests: " + str(len(testslist)))
    
    return Assembly(name, componentslist, connectionslist, testslist)