import pyAgrum as gum
import re
from deepdiff import DeepDiff
import networkx as nx
import itertools
from collections import OrderedDict

def write_to_logfile(log_line):
    # Open a file in write mode
    with open('logfile.txt', 'a') as file:
        # Write a single line
        file.write(log_line + '\n')
        file.flush()
        

# Replace the key while preserving the order
def replace_key_in_ordered_dict(normal_dict, old_key, new_key):
    ordered_dict = OrderedDict(normal_dict)
    if old_key not in ordered_dict:
        raise KeyError(f"Key '{old_key}' not found in dictionary")
    
    # Create a new ordered dict to store the result
    new_ordered_dict = OrderedDict()
    
    # Iterate over the original ordered dict
    for key, value in ordered_dict.items():
        # Replace the old key with the new key
        if key == old_key:
            new_ordered_dict[new_key] = value
        else:
            new_ordered_dict[key] = value
    
    return dict(new_ordered_dict)

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
    
    def getModalityName(self):
        if self.type == "Input":
            return self.getName().split("Inputs")[0]
        if self.type == "Output":
            return self.getName().split("Outputs")[0]        
        
        return self.getName()
        
    def getType(self):
        return self.type
    
    def getVariable(self):
        return self.variable


class Tests:
    def __init__(self, tests):
        self.tests = tests
        self.decision_var = ""
        self.decision_options = []

    def createDecisionVar(self):
        for test_name, details in self.tests.items():
            self.decision_options.append(test_name)


        write_to_logfile(str(self.decision_options))
        self.decision_var = gum.LabelizedVariable("What_to_do", "What is the next step?", self.decision_options)

    def createUtilityNode(self, component):
        found_tests = []
        for test_name, test_info in self.tests.items():
            if component.getName() in test_info['components']:
                found_tests.append([test_name, test_info])

        if found_tests:
            component.createUtilityNode(found_tests)
            
    def GetPriors(self, component):
        utility_node = component.getUtilityNode()
        if utility_node is None:
            return None
        health_node = component.getHealthNode()
        
        priors_found = []
        found_tests = component.found_tests
        for test in found_tests:
            test_name = test[0]
            test_info = test[1]
            # When a test is used in multiple components, lower its costs.
            test_cost = test_info["cost"]/len(test_info['components'])
            
            test_combination = { health_node.getName() : "broken", "What_to_do" : test_name }
            test_util_value = (1.0 / test_cost) * 10000
            priors_found.append([test_combination, test_util_value])

        return priors_found



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
        # Create the output node.
        self.createOutputNode()
        # Create the health node.
        self.createHealthNode()
        # input components
        self.input_components = []
        # output components
        self.output_components = []
        # test info
        self.found_tests = []

    def IsNodeInOtherInputComponent(self, modality_name):
        for component in self.getInputComponents():
            output_nodes = [node for node in component.getNodes() if node.getType() == 'Output']
            for node in output_nodes:
                if node.getModalityName() == modality_name:
                    return True
        return False

    def findNodeByPartOfName(self, partlyname):
        result = None
        for node in self.nodes:
            if partlyname in node.getName():
                result = True
                break
        if result: return True
        else: return False

    def createOutputNode(self):
        # create outputnode
        v = self.specs["Outputs"]["1"]
        varname = str( v['property'] + v['modality']+ "Outputs" + self.name)
        node = Node(varname, "Output", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
        self.nodes.append(node)
            
    def createHealthNode(self):
        # create health node
        v = self.specs["Healths"]["1"]
        varname = str(v["property"])
        # determine if node was given
        if (self.findNodeByPartOfName(varname) == False):
            varname = varname + self.name
            node = Node(varname, "Health", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
            self.nodes.append(node)

    def createUtilityNode(self, found_tests):
            varname = "utility_" + self.name
            node = Node(varname, "Utility", gum.LabelizedVariable(varname, varname, 1))
            self.nodes.append(node)
            self.found_tests = found_tests

    def createInputNodes(self):
        # create input nodes
        for k, v in self.specs["Inputs"].items():
            varname = str( v['property'] + v['modality'])
            # determine if node is an output node of another input component.
            if (self.IsNodeInOtherInputComponent(varname) == False):
                varname = varname + "Inputs" + self.name
                node = Node(varname, "Input", gum.LabelizedVariable(varname, varname, v['propertyvalues']))
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
         
        utility_variable = next((variable for variable in self.getNodeVariables() if re.search("utility", variable.name())), None)
        health_variable = next((variable for variable in self.getNodeVariables() if re.search("health", variable.name())), None)

        if utility_variable is not None and health_variable is not None:
            write_to_logfile(health_variable.name() + " - " + utility_variable.name())
            self.internalconnections.append((health_variable.name(), utility_variable.name()))
    
    # Generate a table with all permuations. Output is set to default value 'no'
    def generateBehaviorSpecs(self):
        keys = []
        possible_values = []

        for k, v in self.specs['Inputs'].items():
            var_name = v["property"] + v["modality"] + "Inputs"
            keys.append(var_name)
            possible_values.append(v["propertyvalues"])
    
        for k, v in self.specs['Healths'].items():
            var_name = "health"
            keys.append(var_name)
            possible_values.append(v["propertyvalues"])

        # Generate all permutations of the possible values
        permutations = list(itertools.product(*possible_values))

        # Initialize the dictionary with empty lists
        data = {key: [] for key in keys}

        # Populate the dictionary with permutations
        for permutation in permutations:
            for key, value in zip(keys, permutation):
                data[key].append(value)

        output_specs = self.specs['Outputs']["1"]
        var_name = output_specs["property"] + output_specs["modality"] + "Outputs"
        data[var_name] = ['no'] * len(data["health"])

        return data

    def mergeGeneratedWithNormal(self, generated_spec, normal_spec):
        matching_indices = []
    
        dict_keys = list(generated_spec.keys())[:-1]
        last_key = list(generated_spec.keys())[-1]
        
        # Iterate over the indices of the data
        for i in range(len(generated_spec[last_key])):
            match = True
            # Check each condition in the condition dictionary
            for key in dict_keys:
                if generated_spec[key][i] != normal_spec[key][0]:
                    match = False
                    break
            if match:
                matching_indices.append(i)
    
        # assumption, ouput is alway yes or no.
        for index in matching_indices:
            generated_spec[last_key][index] = 'yes'
            
        return generated_spec

    # transforms the readable behavior table from specs to a format for use
    # during creation of a potential
    def transformBehaviorTable(self):
        
        generated_spec = self.generateBehaviorSpecs()
        defined_spec = self.specs['Behavior']['normal']
        behaviour_spec = self.mergeGeneratedWithNormal(generated_spec, defined_spec)

        # Replace key values when the node is in an input component.
        new_key_names = []
        for component in self.getInputComponents():
            for l in component.getNodeVariables() :
                if "Output" in l.name():
                    node_name = l.name().split("Outputs")[0]
                    key_values = list(behaviour_spec.keys())
                    old_key_name = [key_value for key_value in key_values if node_name in key_value][0]
                    
                    if old_key_name in behaviour_spec:
                        behaviour_spec = replace_key_in_ordered_dict(behaviour_spec, old_key_name, l.name())
                        new_key_names.append(l.name())

        cptDict = {}
        for k, v in behaviour_spec.items():
            var = k if k in new_key_names else k + self.getName()
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
            elif "Input" in l.name() or "health" in l.name():
                yz.append(l)

        for component in self.getInputComponents():
            for l in component.getNodeVariables():
                if "Output" in l.name():
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
            
    def getUtilityNode(self):
        for node in self.getNodes():
            if (node.getType() == "Utility"):
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
    
    def getInputComponents(self):
        return self.input_components
    
    def getOutputComponents(self):
        return self.output_components

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

class Oopn:
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
