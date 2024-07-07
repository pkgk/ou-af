import pyAgrum as gum
import re
from deepdiff import DeepDiff
import networkx as nx



class Node:
    def __init__(self, name, nodetype, variable):
        self.name = name
        self.type = nodetype                          # input, output, health
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



class SystemHealth:
    def __init__(self, name, healthnodes):
        self.name - name
        


# this class models a component in the system
# the component is defined by it's name and specs (a dict)
# from the specs the internal variables are determined
class Component:
    def __init__(self, name, specs, givennodes):    
        # name component
        self.name = name                   
        # componentspecs type dict
        self.specs = specs         
        # type
        self.type = specs['type']        
        # componentnodes, type Node
        if (len(givennodes) > 0):
            self.nodes = givennodes
        else:
            self.nodes = []                    
        # arcs internal to component, list of tuples
        self.internalconnections = []      
        # turns specs into nodes
        self.createNodes()                 
        # turn specs into internal arcs
        self.setInternalConnections()      
        # prior outputnode, pyAgrum Potential
        self.setPriorOutput()              
        # prior healthnode, pyAgrum Potential
        self.setPriorHealth()              
        # prior inputs, pyAgrum Potential
        self.setPriorInputs()              



    def findNodeByPartOfName(self, partlyname):
        result = None
        for node in self.nodes:
            if partlyname in node.getName():
                result = True
                break
        if result: return True
        else: return False


    def createNodes(self):
        # create outputnode
        v = self.specs["Outputs"]["1"]
        varname = str( v['property'] + v['modality']+ "Outputs" + self.name)
        node = Node(varname, "Output", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
        self.nodes.append(node)

        # create input nodes
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs")
            # determine if node was given and already in list of nodes
            if (self.findNodeByPartOfName(varname) == False):
                varname = varname + self.name
                node = Node(varname, "Input", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
                self.nodes.append(node)
        
        # create health node
        v = self.specs["Healths"]["1"]
        varname = str(v["property"])
        # determine if node was given
        if (self.findNodeByPartOfName(varname) == False):
            varname = varname + self.name
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
    # assumption is health has states ok / broken    and specs contains [0.99, 0.01]
    def setPriorHealth(self):
        # get prior from spec, health has no parents
        p = self.specs["Healths"]["1"]["priorprobability"]
        hnode = self.getHealthNode()
        if (hnode.getPrior != None):        #given node already has prior
            hnode.setPrior(self.generateInstantiationTuples([hnode.getVariable()], p))


    def findInputPriorFromSpecs(self, inputname):
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality']+ "Inputs" + self.name)
            if (varname == inputname):
                return v["priorprobability"]



    def setPriorInputs(self):
        for node in self.getInputNodes():
            if (type(node.getPrior()) != gum.Potential):
                p = self.findInputPriorFromSpecs(node.getName())
                node.setPrior(self.generateInstantiationTuples([node.getVariable()], p))



    # vars: labelized variables
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
    
    def getType(self):
        return self.type

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
    
    def getSpecs(self):
        return self.specs







# class Connection models connections between component in the system
# a connection is defined by it's name, specs (dict) and start + end components

class Connection:
    def __init__(self, name, specs, startcomponent, endcomponent, healthnode):
        self.name = name                                     # name of the connection
        self.specs = specs                                   # dict specifying properties of connection
        self.startcomponent = startcomponent
        self.endcomponent = endcomponent
        self.startnode = None                                # node that is starting point for connection
        self.endnode = None                                  # node that is ending point for connection
        self.healthnode = healthnode
        self.cptendcomponent = None
        self.setHealthVariable()
        self.setPriorHealth()
        self.setStartEndNodes()
        self.setCptEndNode()                                 # potentional for cpt

        
    # create pyAgrum labelized variable used when adding health for connection to diagram
    def setHealthVariable(self):
        if (self.healthnode == None):
            label = "health" + self.name
            v = self.specs["Healths"]["1"]
            if (v != None):
                self.healthnode = Node(label, "Health", gum.LabelizedVariable(label, label, v['propertyvalues']))
            else: print("Connection/setHealthVariable: no description for health " + self.name)

    # set the prior of the health node
    # assumption is health has states ok / broken and specs contains [0.99, 0.01]
    def setPriorHealth(self):
        # get prior from spec, health has no parents
        p = self.specs["Healths"]["1"]["priorprobability"]
        if (p != None):
            self.healthnode.setPrior(self.generateInstantiationTuples([self.healthnode.getVariable()], p))
        else: print("Connection/setPriorHealth: no description for prio of health " + self.name)


    # create Potential for variables in vars with priors from list
    # Instantiation is index for Potential
    # vars: variables list to fill Potential
    # priors: given priors
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


    # determine start and end nodes by taking beginning of nodename from specs + component name
    def setStartEndNodes(self):
        startnodename = str(self.specs['start'] + self.startcomponent.getName())
        for node in self.startcomponent.getNodes():
            if (node.getName() == startnodename): 
                self.startnode = node
                break

        endnodename = str(self.specs['end'] + self.endcomponent.getName())
        for node in self.endcomponent.getNodes():
            if (node.getName() == endnodename): 
                self.endnode = node
                break


    def keyToNodeName(self, key):
        if re.search(key, self.startnode.getName()): return self.startnode.getName()
        if re.search(key, self.endnode.getName()): return self.endnode.getName()
        if re.search(key, self.healthnode.getName()): return self.healthnode.getName()

    # transforms the readable behavior table from specs to a format for use
    # during creation of a potential
    def transformBehaviorTable(self):
        cptDict = {}
        for k, v in self.specs['Behavior']['normal'].items():
            var = self.keyToNodeName(k)
            count = 0
            for e in v:
                if count in cptDict:
                    d = cptDict[count]
                    d[var] = e
                else:
                    cptDict[count] = {var: e}
                count = count + 1
        return cptDict


    # determine probability table for end node
    def setCptEndNode(self):
        if (type(self.startnode) == Node and type(self.endnode) == Node):
            # first extend potential
            potential = self.endnode.getPrior()
            labelvar = self.startnode.getVariable()
            potential.add(labelvar)
            potential.add(self.healthnode.getVariable())
        else: print("Connection/setCptEndNode: start or endnode for connection not set " + self.name)
        
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
    def getConnectionNodes(self):
        return (self.startnode.getName(), self.endnode.getName())
    def getHealthNode(self):
        return self.healthnode    
    def getSpecs(self):
        return self.specs
    



# class assembly contains objects for all part of the system: components, connections, tests
# Oopn also supports copying part of the network to support type 2 tests
# oopn also support setting a system health variable

class Oopn:
    def __init__(self, name, components, connections, tests):
        self.name = name
        self.components = components
        self.connections = connections
        self.tests = tests
        self.systemhealth = None

    def getName(self):
        return self.name
    def getComponents(self):
        return self.components
    def getConnections(self):
        return self.connections
    def getTests(self):
        return self.tests

    
    def findComponentFromNodeName(self, nodename):
        foundcomp = None
        for comp in self.components:
            for node in comp.getNodes():
                if (nodename == node.getName()):
                    foundcomp = comp
                    break
        return foundcomp
    
    def addComponent(self, component):
        if (type(component) == Component):
            self.components.append(component)
        else: print("error: type not component, cannot add to list of components")
                
    def addConnection(self, con):
        if (type(con) == Connection):
            self.connections.append(con)
        else: print("error adding connection, type not correct")

    
    def getAllNodeNames(self):
        nodenamelist = []
        for c in self.components:
            for n in c.getNodes():
                nodenamelist.append(n.getName())
        return nodenamelist

    def getAllConnections(self):
        connectionlist = [] 
        for c in self.components:
            for ic in c.getInternalConnections():
                connectionlist.append(ic)
        for con in self.connections:
            connectionlist.append(con.getConnectionNodes())
        return connectionlist
    

    def setSystemHealth(self):
        pass

    # helper to copying components
    def determinePathStartToFinish(self, nodes, connections, start, finish):
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(connections)
        if (nx.has_path(G, start, finish)):
            return nx.shortest_path(G, start, finish)
        else: print('Error no path available')

    # derive a list of unique components in path
    def determineComponentsInNodesPath(self, path):
        componentlist = []
        for nodename in path:
            component = self.findComponentFromNodeName(nodename)
            componentnodes = component.getNodes()
            for cn in componentnodes:
                if (nodename == cn.getName()):
                    if (len(componentlist) > 0):
                        if (componentlist[-1] != component.getName()):
                            componentlist.append(component.getName())
                    else:
                        componentlist.append(component.getName())            
        return componentlist

    def findComponentByName(self, name):
        for component in self.getComponents():
            if component.getName() == name:
                return component
            

    # enable copying of nodes due to the type 2 test
    def copyPathType2Test(self, startnode, endnode):
        # create DAG and determine path from startnode to finishnode
        nodepath = self.determinePathStartToFinish(self.getAllNodeNames(),self.getAllConnections(), startnode, endnode )

        # add copied components to OOPN
        # first determine all components part of path and loop one by one
        for componentname in self.determineComponentsInNodesPath(nodepath):
            component = self.findComponentByName(componentname)
            # determine nodes not in nodepath > mark for reuse when creating copy
            reusenodes = []
            for node in component.getNodes():
                if (node.getName() in nodepath):
                    pass
                else:
                    reusenodes.append(node)
            # determine name of copied component
            newname = componentname + "copy"
            print("adding component: " + newname)
            # create a copy component and add to oopn
            self.addComponent(Component(newname, component.getSpecs(), reusenodes))
    
        # add copied connections to OOPN
        for i in range(0, len(nodepath)-1):
            # create a connection tuple with next node
            nodepathtuple = (nodepath[i], nodepath[i+1])
            # check if tuple is existing connection, if so create a copy
            for con in self.getConnections():
                if nodepathtuple == con.getConnectionNodes():
                    startcomponent = self.findComponentFromNodeName(str(nodepathtuple[0]) + "copy")
                    endcomponent = self.findComponentFromNodeName(str(nodepathtuple[1]) + "copy")
                    healthnode = con.getHealthNode()
                    print("adding connection " +  con.getName() + 'copy' + " between: " + startcomponent.getName() + " and " + endcomponent.getName() + " with healthnode: " + healthnode.getName())
                    newcon = Connection(con.getName() + 'copy', con.getSpecs(), startcomponent, endcomponent, healthnode)
                    self.addConnection(newcon)
