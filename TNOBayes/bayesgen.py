import os
from bidict import bidict

from concepts import *
from connectors import * # for coloring the nodes
from components import WireJoint # needs special treatment because of short-to-ground failure mode
from connections import Wire, Ability # require special treatment

from bayesserver import *
from jpype import JArray, JInt, JObject, java #type: ignore

TN = TypeVar("TN", Component, Connector, Connection)

NodeDictOrBidict = dict[TN, Node] | bidict[TN, Node]

class NodeMapping:
    """ Stores the mapping of each component, connector, and connection to the corresponding node."""
    def __init__(self, components: NodeDictOrBidict[Component], connectors: NodeDictOrBidict[Connector], connections: NodeDictOrBidict[Connection]):
        self.componentNodes: bidict[Component, Node] = bidict(components) if isinstance(components, dict) else components
        self.connectorNodes: bidict[Connector, Node] = bidict(connectors) if isinstance(connectors, dict) else connectors
        self.connectionNodes: bidict[Connection, Node] = bidict(connections) if isinstance(connections, dict) else connections

def colorProperty(colorCode: str):
    """ Returns the custom property that BayesServer adds to nodes for visualization in the UI """
    colorProp = bayesServer.CustomProperty("12c0d606-59ee-4282-a56e-2aed2f57c495", colorCode)
    return colorProp

def addGroup(network: Network, groupName:str, colorCode:str) -> None:
    """ Adds a node group definition to the network and assigns it a color """
    nodeGroup = bayesServer.NodeGroup(groupName)
    nodeGroup.getCustomProperties().add(colorProperty(colorCode))
    network.getNodeGroups().add(nodeGroup)

def addNodeModality(node: Node, connector: Connector):
    """ Add the connector node to a node group to see the modality color coded in BayesServer """
    if isinstance(connector, SheetHandler):
        node.getGroups().add("Material")
    elif isinstance(connector, Hole):
        node.getGroups().add("Air")
    elif isinstance(connector, Plug): 
        node.getGroups().add("Electrical")
    elif isinstance(connector, Shaft): 
        node.getGroups().add("Mechanical")
    elif isinstance(connector, ComputingResource):
        node.getGroups().add("ComputingResource")
    elif isinstance(connector, ErrorMessage):
        node.getGroups().add("ErrorMessage")
    elif isinstance(connector, LightPlug):
        node.getGroups().add("Radiation")
    elif isinstance(connector, Heat):
        node.getGroups().add("Radiation")
    elif isinstance(connector, (Water, Moisture)):
        node.getGroups().add("Water")
    elif isinstance(connector, (Trigger, Presence)):
        node.getGroups().add("Trigger")
    elif isinstance(connector, Indicator):
        node.getGroups().add("Indicator")
    elif isinstance(connector, CapabilityPort):
        node.getGroups().add("Capability")
    elif isinstance(connector, FuelPlug):
        node.getGroups().add("Fuel")
    else:
        #assert False, f"Unknown modality {type(connector)}"
        defaultModality = "Material"
        #print(f"Unknown modality {type(connector)}, using the default {defaultModality} instead")
        node.getGroups().add(defaultModality)


def reverseName(name: str) -> str:
    """ Reverse the name. 
    
    This is useful for display in BayesServer as these nodes only show the first part of the name and 
    we want that to be the most significant.
    The first part is removed because it is always the same and clutters the display
    """
    p = name.split(SPLITCHAR)
    q = SPLITCHAR.join(n.strip() for n in reversed(p[1:]))

    return q

def createNode(name:str, states:List[str], reversedName:bool =False):
    """ Creates a node with given name and states.

    Name is reversed for better viewing in BayesServer GUI. 
    Width and Height of the node is estimated to get reasonable display when auto-layouting in BayesServer
    """
    node = bayesServer.Node(reverseName(name) if reversedName else name, states)
    maxStateNameLength = max(len(strname) for strname in states)
    width = max(160, min(220, maxStateNameLength*20))
    height = 70+(len(states)-2)*18
    bounds = bayesServer.Bounds(0, 0, width, height)
    node.setBounds(bounds)

    return node

def createVariable(name:str, states:List[str]) -> Variable:
    variable = bayesServer.Variable(reverseName(name), states)
    return variable

def createNodeForVariables(name:str, *variables:Variable, reversedName:bool =False):
    """ Creates a node with given name and states.

    Name is reversed for better viewing in BayesServer GUI. 
    Width and Height of the node is estimated to get reasonable display when auto-layouting in BayesServer
    """
    node = bayesServer.Node(reverseName(name) if reversedName else name, *variables)
    nrVariables = len(variables)
    stateNames = [state.getName() for variable in variables for state in variable.getStates()]

    maxStateNameLength = max(len(strname) for strname in stateNames)
    width = max(160, min(220, maxStateNameLength*20))
    height = 70+(len(stateNames)-2)*18 + nrVariables*36
    bounds = bayesServer.Bounds(0, 0, width, height)
    node.setBounds(bounds)

    return node


def setPriors(node: Node, failures: Sequence[Failure]):
    """ Sets the prior probabilities for a node based on the specified failure mode probabilities
    """
    normalProb = 1.0 - sum(failure.prior for failure in failures)
    table = node.newDistribution().getTable()
    tableAccessor = bayesServer.TableAccessor(table, [node])
    tableAccessor.set(0, normalProb)
    for i,failure in enumerate(failures):
        tableAccessor.set(i+1, failure.prior)
    
    node.setDistribution(table)


def isClauseEqual(clause: Clause, state: int) -> bool:
    return (clause == ANY) or (clause.value-1 == state)  #type: ignore

def isOutputEqual(inputStates: List[int], outcome: Consequence, outputState:int) -> bool:
    if isinstance(outcome, SAME):
        assert 1 <= outcome.index <= len(inputStates), f"SAME must be referring to existing input but is out of range: {outcome.index} is not within [1,{len(inputStates)}]"
        return inputStates[outcome.index-1] == outputState
    else:        
        return outcome.value-1 == outputState #type: ignore

def matchesConnectionRelation(inStates: Sequence[int], outStates: Sequence[int], relation: Relation) -> Prob:
    """ Find the probability of a rule that matches the given input and output state 
    
    Usually, the probabilty will either be 0.0 or 1.0 but we allow for probabilistic relations
    In case of probabilistic relations, for a given output state multiple rules can match. We then sum the probabilities of the matching rules.
    """
    # for connections only, so there is only one input and one output node, but there could be more variables
    probability = 0.0
    conditionMatched = False
    assert len(relation) > 0, f"Relation must have at least 1 rule but has {len(relation)}"
    for rule in relation:
        assert len(rule) == 2 or len(rule) == 3, f"expect rule to have 2 or 3 elements but has {len(rule)}"
        if len(rule) == 2:
            condition, outcomes = rule #type: ignore  See https://stackoverflow.com/questions/66242131/unpacking-tuple-gives-tuple-size-mismatch-error
            prob = 1.0
        else:
            condition, outcomes, prob = rule #type: ignore
            assert condition != ELSE and condition != ALWAYS, f"ELSE or ALWAYS conditions cannot have an assigned probability, but is {prob}"
        assert 0.0 <= prob <= 1.0, f"Rule probability must be between 0 and 1 but is {prob}"
        if condition == ELSE:
            if not conditionMatched:
                # Else clause needs to be evaluated because no other condition matched
                # Python enums start values at 1 (?!)
                if all(isOutputEqual(inStates, outcome, outState) for outcome, outState in zip(outcomes, outStates)): #type: ignore
                    probability += prob
        else:
            if all(isClauseEqual(clause, inState) for clause, inState in zip(condition, inStates)): 
                conditionMatched = True
                if all(isOutputEqual(inStates, outcome, outState) for outcome, outState in zip(outcomes, outStates)): #type: ignore
                    probability += prob

    assert 0.0 <= probability <= 1.0, f"Total probabilty out of range ({probability})"
    return probability


def matchesComponentRelation(inputStates: List[int], outputIndex: int, outputStates: List[int], relation: Relation) -> Prob:
    """ Find the probability of a rule that matches the given input states and output states 
    
    inputStates : list of the state numbers of all input variables
    outputIndex : index of the output variable
    outputStates : list of state number for all the variables of a single output node

    Usually, the probability will either be 0.0 or 1.0, but we allow for probabilistic relations
    """
    probability = 0.0
    conditionMatched = False
    assert len(relation) > 0, f"Relation must have at least 1 rule but has {len(relation)}"
    for rule in relation:
        assert len(rule) == 2 or len(rule) == 3, f"expect rule to have 2 or 3 elements but has {len(rule)}"
        if len(rule) == 2:
            conditions, outcomes = rule 
            prob = 1.0
        else:
            conditions, outcomes, prob = rule 
            assert conditions != ELSE and conditions != ALWAYS, f"ELSE or ALWAYS conditions cannot have an assigned probability, but is {prob}"
        assert 0.0 <= prob <= 1.0, f"Rule probability must be between 0 and 1 but is {prob}"

        filteredOutcomes = outcomes[outputIndex:outputIndex+len(outputStates)]  # only the variables for this particular Output node
        if conditions == ELSE:
            if not conditionMatched:
                # Else clause needs to be evaluated because no other condition matched
                # Python enums start values at 1 (?!)
                if all(isOutputEqual(inputStates, outcome, outputState) for outcome, outputState in zip(filteredOutcomes, outputStates)):
                    probability += prob
        else:
            if all(isClauseEqual(clause, inputState) for clause, inputState in zip(conditions, inputStates)):
                conditionMatched = True
                if all(isOutputEqual(inputStates, outcome, outputState) for outcome, outputState in zip(filteredOutcomes, outputStates)):
                    probability += prob

    assert 0.0 <= probability <= 1.0,  f"Total probabilty out of range ({probability})"
    return probability

    
def nodeToVariables(*nodes: Node) -> List[Variable]:
    variables = [variable for node in nodes for variable in node.getVariables()]
    return variables


def setConnectionCPT(connection: Connection, healthNode: Node, connectorNodes: Dict[Connector, Node]):
    """ Set the CPT of connection output (this is a component input)
    """
    #print(f"Setting CPT for {connection.getName()}")
    node = connectorNodes[connection.output]
    table = node.newDistribution().getTable()
    #print(f"Table size {table.size()}")
    inputVariables = nodeToVariables(connectorNodes[connection.input])
    outputVariables = nodeToVariables(node)
    nrProperties = len(inputVariables)
    assert nrProperties == len(outputVariables), f"Properties of connection do not match {nrProperties} ≠ {len(outputVariables)}"
    variables = nodeToVariables(healthNode)+inputVariables+outputVariables
    tableIterator = bayesServer.TableIterator(table, variables)
    IntArrayClass = JArray(JInt)
    states = IntArrayClass(len(variables))

    if connection.normal is None:
        # no failures, one-on-one passing of properties
        for _ in range(tableIterator.size()):
            tableIterator.getStates(states)
            if all(inp == outp for inp, outp in zip(states[1:1+nrProperties], states[1+nrProperties:1+2*nrProperties])):
                tableIterator.setValue(1.0)
            else:
                tableIterator.setValue(0.0)
            tableIterator.increment()
        
        print(f"Setting distribution for {node.getName()}. Connection has no failure modes")
        node.setDistribution(table)

    elif len(connection.failures) == 0:
        # no failures specified. Everything not normal is considered a generic broken
        assert nrProperties == 1, f"Multiple properties require failure mode specification. Number of properties of {connection.getName()} is {nrProperties}"
        for _ in range(tableIterator.size()):
            tableIterator.getStates(states)
            prob = matchesConnectionRelation(states[1:1+nrProperties], states[1+nrProperties:1+2*nrProperties], connection.normal.relation) == (states[0] == 0)
            tableIterator.setValue(prob)
            tableIterator.increment()

        print(f"Setting distribution for {node.getName()}. Connection has default broken failure mode")
        node.setDistribution(table)

    else:
        # failures specified. Insert logic accordingly.
        for _ in range(tableIterator.size()):
            tableIterator.getStates(states)
            if states[0] == 0:
                relation = connection.normal.relation
            else:
                relation = connection.failures[states[0]-1].relation
            prob = matchesConnectionRelation(states[1:1+nrProperties], states[1+nrProperties:1+2*nrProperties], relation)
            tableIterator.setValue(prob)
            tableIterator.increment()

        print(f"Setting distribution for {node.getName()}. Connection has {len(connection.failures)} failure modes")
        node.setDistribution(table)
        
def setTrivialConnectionCPT(connection: Connection, connectorNodes: Dict[Connector, Node]):
    """ Set the CPT of connection output (this is a component input) of a never failing connection
    """
    print(f"Setting trivial CPT for {connection.getName()}")
    node = connectorNodes[connection.output]
    table = node.newDistribution().getTable()
    #print(f"Table size {table.size()}")
    tableIterator = bayesServer.TableIterator(table, [connectorNodes[connection.input], node])
    IntArrayClass = JArray(JInt)
    states = IntArrayClass(2)

    # no failures, one-on-one passing of properties
    for entry in range(tableIterator.size()):
        tableIterator.getStates(states)
        if states[0] == states[1]:
            tableIterator.setValue(1.0)
        else:
            tableIterator.setValue(0.0)
        tableIterator.increment()
        
        print(f"Setting distribution for {node.getName()}. Connection has no failure modes")
    node.setDistribution(table)


def setComponentCPT(component: Component, healthNode: Node, connectorNodes: Dict[Connector, Node]):
    """ Set the CPT of the component output nodes based on the component relation specification 
    """ 
    #print(f"Setting CPT for {component.name}")
    assert component.normal is not None, f"Component {component.name} ({type(component)}) lacks normal behavior specification"

    inputNodes = [connectorNodes[input] for input in component.getInputs()]
    inputVariables = nodeToVariables(*inputNodes)
    healthVariables = nodeToVariables(healthNode)
    firstOutputIndex = len(healthVariables)+len(inputVariables)
    outputIndex = 0
    for output in component.getOutputs():
        node = connectorNodes[output]
        table = node.newDistribution().getTable()
        outputVariables = nodeToVariables(node)
        nrOutputVariables = len(outputVariables)
        variables = healthVariables+inputVariables+outputVariables
        tableIterator = bayesServer.TableIterator(table, variables)
        IntArrayClass = JArray(JInt)
        states = IntArrayClass(len(variables))

        if len(component.failures) == 0:
            # everything that is not normal is broken
            # if an output has more than 2 states it is ambiguous what the broken state would be, so we assert.
            assert all(len(outvariable.getStates()) == 2 for outvariable in outputVariables), f"Cannot reconstruct normal behavior for {component.name} without failure specification because it has multiple states"  #type: ignore
            for _ in range(tableIterator.size()):
                tableIterator.getStates(states)
                prob = matchesComponentRelation(states[1:-nrOutputVariables], outputIndex, states[firstOutputIndex:firstOutputIndex+nrOutputVariables], component.normal.relation)
                if states[0]==0: 
                    tableIterator.setValue(prob)
                else:
                    tableIterator.setValue(1.0 - prob)
                tableIterator.increment()

            print(f"Setting distribution for {node.getName()}. Component has default broken failure mode")
            node.setDistribution(table)

        else:
            for _ in range(tableIterator.size()):
                tableIterator.getStates(states)
                if states[0] == 0: 
                    relation = component.normal.relation
                else:
                    relation = component.failures[states[0]-1].relation
                prob = matchesComponentRelation(states[1:-nrOutputVariables], outputIndex, states[firstOutputIndex:firstOutputIndex+nrOutputVariables], relation)
                #print(f"{[state for state in states]}  {prob}")
                tableIterator.setValue(prob)
                tableIterator.increment()

            print(f"Setting distribution for {node.getName()}. Component has {len(component.failures)} failure modes")
            node.setDistribution(table)

        outputIndex += nrOutputVariables
    
def createConnectorNodes(module: Module, network: Network, connectorNodes: Dict[Connector,Node]):
    for connector in module.getConnectors():
        #print(f"Creating connector {connector.name}")
        properties = list(connector.getProperties())
        #assert len(properties) == 1, f"Number of properties of {type(connector)} must (currently) be 1 but is {len(properties)}" # TODO: support multiple properties

        variables:List[Variable] = []
        for property in properties:
            name, ttype = property
            propertyValues = [p.name.lower() for p in list(ttype)] # type: ignore as this is a bug in pytype I believe. We know ttype is an Enum and list is defined on Enum
            variable = createVariable(connector.extendName(name), propertyValues)
            variables.append(variable)

        node = createNodeForVariables(connector.name, *variables, reversedName=True)
        network.getNodes().add(node)
        connectorNodes[connector] = node
        addNodeModality(node, connector)

    
def generateCapability(capability:Capability, network:Network, componentNodes: Dict[Component, Node], connectorNodes: Dict[Connector, Node]):
    # introduce node TODO: support multiple levels of capability
    # createConnectorNodes(capability, network, connectorNodes)
    propertyValues = ["can", "cannot"]
    node = createNode(capability.name, propertyValues)
    network.getNodes().add(node)
    node.getGroups().add("Capability")
    connectorNodes[capability] = node

def generateComponent(component: Component, network: Network, componentNodes: Dict[Component, Node], connectorNodes: Dict[Connector, Node]):
    """ Generates the nodes for a component: all inputs, all outputs, and a health node

        The CPT of the health node is determined by the probabilities of the failure modes.
        The CPT of the output nodes is determined by the specified relations (normal + failures)
        The CPT of the input nodes is not set here, but is the result of creating the connections
    """
    # All connectors
    createConnectorNodes(component, network, connectorNodes)

    # Add links from all inputs to all outputs
    for inputConnector in component.getInputs():
        for outputConnector in component.getOutputs():
            #print(f"Linking {inputConnector} to {outputConnector}")
            link = bayesServer.Link(connectorNodes[inputConnector], connectorNodes[outputConnector])
            network.getLinks().add(link)
        

    # Health node
    states = ["OK"]
    if component.normal is not None and len(component.failures) == 0:
        states.append("broken")
    else:
        states.extend(failure.name for failure in component.failures)
    healthNode = createNode(component.extendName("Health"), states, reversedName=True)
    healthNode.getGroups().add("Component")
    network.getNodes().add(healthNode)
    componentNodes[component] = healthNode

    setPriors(healthNode, component.failures)

    # Add links from health to all outputs
    for outputConnector in component.getOutputs():
        #print(f"Linking Health to {outputConnector}")
        outputNode = connectorNodes[outputConnector]
        link = bayesServer.Link(healthNode, outputNode)
        network.getLinks().add(link)

    # add CPT for this component, relating inputs+health to outputs
    setComponentCPT(component, healthNode, connectorNodes)

def setStateCPT(stateNode:Node, state:State, connectorNodes: Dict[Connector, Node]):
    """ Translate transitions into a full CPT for the state node
    """
    print(f"Setting CPT for {state.name}")
    assert state.stateProbs is not None, f"State {state.name} ({type(state)}) lacks state specification" 
    assert len(state.stateProbs) > 0, f"Relation must have at least 1 rule but has {len(state.stateProbs)}"

    table = stateNode.newDistribution().getTable()
    #print(f"Table size {table.size()}")
    inputNodes = [connectorNodes[input] for input in state.getInputs()]
    tableIterator = bayesServer.TableIterator(table, inputNodes+[stateNode])
    IntArrayClass = JArray(JInt)
    states = IntArrayClass(len(inputNodes)+1)

    for _ in range(tableIterator.size()):
        tableIterator.getStates(states)
        for conditions, probs in state.stateProbs:
            assert conditions is not None and len(conditions) > 0, f"Illegal rule specification for {state.name}"
            if all(clause.value-1 == states[idx] for idx, clause in enumerate(conditions)):  #type: ignore
                probability = probs[states[-1]]
                assert 0.0 <= probability <= 1.0, f"Probability out of range ({probability})"
                tableIterator.setValue(probability)

        tableIterator.increment()

    print(f"Setting state distribution for {stateNode.getName()}")
    stateNode.setDistribution(table)

def setStateOutputCPT(state:State, outputIndex:int, stateNode:Node, connectorNode:Node):
    print(f"Setting CPT for {connectorNode.getName()} in state {state.name}")
    assert state.normal is not None, "No normal behavior specified"
    assert len(state.normal.relation) > 0, f"State {state.name} has not output relation defined"

    table = connectorNode.newDistribution().getTable()
    #print(f"Table size {table.size()}")
    tableIterator = bayesServer.TableIterator(table, [stateNode,connectorNode])
    IntArrayClass = JArray(JInt)
    states = IntArrayClass(2)

    for _ in range(tableIterator.size()):
        tableIterator.getStates(states)
        prob = matchesComponentRelation(states[:1], outputIndex, states[outputIndex+1], state.normal.relation)
        tableIterator.setValue(prob)
        tableIterator.increment()

    print(f"Setting state output {outputIndex} distribution for {stateNode.getName()}")
    connectorNode.setDistribution(table)
    

def generateState(state:State, network:Network, componentNodes: Dict[Component, Node], connectorNodes: Dict[Connector, Node]):
    # create connectors
    createConnectorNodes(state, network, connectorNodes)

    # create node
    assert state.state is not None, f"No states defined for {state}"
    stateNode = createNode(state.name, [s.name for s in state.state], reversedName=True) #type: ignore
    network.getNodes().add(stateNode)

    # link all inputs to node
    for input in state.getInputs(False):
        link = bayesServer.Link(connectorNodes[input], stateNode)
        network.getLinks().add(link)
    
    # set CPT
    setStateCPT(stateNode, state, connectorNodes)
    
    # link node to outputs
    for idx, output in enumerate(state.getOutputs(False)):
        link = bayesServer.Link(stateNode, connectorNodes[output])
        network.getLinks().add(link)
        
        # set output CPT's
        setStateOutputCPT(state, idx, stateNode, connectorNodes[output])

def generateModules(module: Module, network: Network, componentNodes: Dict[Component, Node], connectorNodes: Dict[Connector, Node]):
    """ Recursively creates health nodes for all components """
    #print(f"Generating bayes net for {module.name}")
    if isinstance(module, Component):
        generateComponent(module, network, componentNodes, connectorNodes)
            
    elif isinstance(module, Capability):
        generateCapability(module, network, componentNodes, connectorNodes)

    elif isinstance(module, Assembly):
        for internalModule in module.getModules():
            generateModules(internalModule, network, componentNodes, connectorNodes)

    elif isinstance(module, State):
        generateState(module, network, componentNodes, connectorNodes)

    else:
        raise NotImplementedError(f"Generation for this module {module.name} of type {type(module)} not yet implemented")

def findComponent(connector: Connector, module: Module) -> Component:
    """ Find the component of a connector"""
    # this is always the parent
    component = connector.parent
    assert isinstance(component, Component)
    return component

def isFirstWireInCableTree(connection: Connection, module: Module):
    """ Checks if a connection is the first wire in a cable tree by looking at the type of the connection and the input and output components"""
    return isinstance(connection, Wire) and \
           isinstance(findComponent(connection.output, module), WireJoint) and \
           not isinstance(findComponent(connection.input, module), WireJoint)

def insertCableTreeNode(wire: Wire, wireNode: Node, network: Network, connectorNodes: Dict[Connector,Node], cableTreeNodes: Dict[Wire, Node]):
    """ Inserts a Cable Tree node that can capture a short-to-ground in a cable tree. The wire provided is the first wire in the cable tree """
    # Create cable tree node
    cableTreeNode = createNode(f"Cable tree power of {wire.getName()}", ["yes", "no"])
    cableTreeNode.getGroups().add("Electrical")
    network.getNodes().add(cableTreeNode)
    # Create link from wire input to the cable tree node
    link = bayesServer.Link(connectorNodes[wire.input], cableTreeNode)
    network.getLinks().add(link)
    # Create link from cable tree node to wire output
    wireOutputNode = connectorNodes[wire.output]
    link = bayesServer.Link(cableTreeNode, wireOutputNode)
    network.getLinks().add(link)
    # Create link from wire health to cable tree node
    link = bayesServer.Link(wireNode, cableTreeNode)
    network.getLinks().add(link)

    cableTreeNodes[wire] = cableTreeNode

    # Set CPT of the wire output node
    table = wireOutputNode.newDistribution().getTable()
    linksIn = wireOutputNode.getLinksIn()
    parentNodes = [link.getFrom() for link in linksIn]
    assert len(parentNodes) == 2, f"Expected 2 parents but found {len(parentNodes)}" 
    tableIterator = bayesServer.TableIterator(table, [wireOutputNode]+parentNodes)
    IntArrayClass = JArray(JInt)
    states = IntArrayClass(len(parentNodes)+1)
    # TODO: implement AND-logic less clumsy
    for entry in range(tableIterator.size()):
        tableIterator.getStates(states)
        if states[0] == 0:
            if all(state == 0 for state in states[1:]):
                tableIterator.setValue(1.0)
            else:
                tableIterator.setValue(0.0)
        elif states[0] == 1:
            if any(state > 0 for state in states[1:]):
                tableIterator.setValue(1.0)
            else:
                tableIterator.setValue(0.0)
        tableIterator.increment()

    wireOutputNode.setDistribution(table)


def generateConnections(module: Module, network: Network, componentNodes: Dict[Component, Node], connectorNodes: Dict[Connector, Node], connectionNodes: Dict[Connection, Node], cableTreeNodes: Dict[Wire, Node]):
    """ Introduces Health nodes for all connections and sets the CPT's for the health node and the output
    """
    print(f"Generating all connections for {module.name}")
    for connection in module.getConnections(recursive=True):
        if isinstance(connection, Ability):
            # abilities cannot fail
            link = bayesServer.Link(connectorNodes[connection.input], connectorNodes[connection.output])
            network.getLinks().add(link)
            setTrivialConnectionCPT(connection, connectorNodes)
        else:
            # introduce health node for the connection
            normalProb = 1.0 - sum(failure.prior for failure in connection.failures)
            states = ["OK"]
            if connection.normal is not None and len(connection.failures) == 0:
                states.append("broken")
            else:
                states.extend(failure.name for failure in connection.failures)
            healthNode = createNode("Health "+connection.getName(), states) 
            network.getNodes().add(healthNode)
            healthNode.getGroups().add("Connection")
            addNodeModality(healthNode, connection.output)
            connectionNodes[connection] = healthNode
        
            # Set health prior probability
            table = healthNode.newDistribution().getTable()
            tableAccessor = bayesServer.TableAccessor(table, [healthNode])
            tableAccessor.set(0, normalProb)
            for i,failure in enumerate(connection.failures):
                tableAccessor.set(i+1, failure.prior)
        
            healthNode.setDistribution(table)

            # Add link from Health to Output
            link = bayesServer.Link(healthNode, connectorNodes[connection.output])
            network.getLinks().add(link)

            # If this is the first Wire in a cabletree, we have to introduce a CableTree node
            if isFirstWireInCableTree(connection, module):
                assert isinstance(connection, Wire), f"Expected Wire but got {type(connection)}"
                insertCableTreeNode(connection, healthNode, network, connectorNodes, cableTreeNodes)
            else:
                # link from Input to Output
                link = bayesServer.Link(connectorNodes[connection.input], connectorNodes[connection.output])
                network.getLinks().add(link)

                setConnectionCPT(connection, healthNode, connectorNodes)
        
def generateHealthLinks(module, network, componentNodes, connectorNodes, connectionNodes: Dict[Connection,Node]):
    for capability in module.getCapabilities(recursive=False):
        capabilityNode = connectorNodes[capability]
        dummyConnectionNodes = []
        dummyConnections = []
        componentHealthNodes = []
        for unreliable, goodstates in capability.inputs:
            if isinstance(unreliable, Connection):
                connection = unreliable
                # introduce Health node on the fly if it is a dummy connection (otherwise it already exists)            
                try:
                    healthNode = connectionNodes[connection]
                except KeyError:
                    # does not exist so create it
                    states = ["OK"]
                    if connection.normal != None and len(connection.failures) == 0: 
                        states.append("broken")
                    else:
                        states.extend(failure.name for failure in connection.failures)
                    healthNode = createNode("Health "+connection.getName(), states) 
                    healthNode.getGroups().add("Connection")
                    network.getNodes().add(healthNode)
        
                    normalProb = 1.0 - sum(failure.prior for failure in connection.failures)
                    table = healthNode.newDistribution().getTable()
                    tableAccessor = bayesServer.TableAccessor(table, [healthNode])
                    tableAccessor.set(0, normalProb)
                    for i,failure in enumerate(connection.failures):
                        tableAccessor.set(i+1, failure.prior)
        
                    healthNode.setDistribution(table)

                link = bayesServer.Link(healthNode, capabilityNode)
                network.getLinks().add(link)
                dummyConnectionNodes.append(healthNode)
                dummyConnections.append((connection, goodstates))

            elif isinstance(unreliable, Component):
                componentNode = componentNodes[unreliable]
                link = bayesServer.Link(componentNode, capabilityNode)
                network.getLinks().add(link)
                componentHealthNodes.append(componentNode)

            elif isinstance(unreliable, Capability):
                capabilityInNode = connectorNodes[unreliable]
                link = bayesServer.Link(capabilityInNode, capabilityNode)
                network.getLinks().add(link)
                componentHealthNodes.append(capabilityInNode)
                
            else:
                raise TypeError(f"Type {type(unreliable)} not supported")

        # now set the CPT of the capability node
        table = capabilityNode.newDistribution().getTable()
        tableIterator = bayesServer.TableIterator(table, [capabilityNode]+dummyConnectionNodes+componentHealthNodes)
        IntArrayClass = JArray(JInt)
        states = IntArrayClass(1+len(dummyConnectionNodes)+len(componentHealthNodes))
        for entry in range(tableIterator.size()):
            tableIterator.getStates(states)
            isgood = all(state == 0 for state in states[1+len(dummyConnectionNodes):]) # component health nodes
            if isgood: # also check connection health nodes
                for idx, (connection, goodstates) in enumerate(dummyConnections):
                    goodstateNumbers = [0]
                    for nr, failure in enumerate(connection.failures):
                        if failure.name in [goodstates]:
                            goodstateNumbers.append(nr+1)
                    if states[idx+1] not in goodstateNumbers:
                        isgood = False
            if (states[0] == 0 and isgood) or (states[0] == 1 and not isgood):
                tableIterator.setValue(1.0)
            else:
                tableIterator.setValue(0.0)
            tableIterator.increment()

        capabilityNode.setDistribution(table)

    for m in module.getAssemblies(recursive=False):
        generateHealthLinks(m, network, componentNodes, connectorNodes, connectionNodes)
        

def isStateImpossible(connector: Connector, states: List[int]) -> bool:
    """ Returns True iff the state is impossible for this connector.

        This method relies on the order of the properties defined.
    """

    impossible = False
    modality = connector.getModality()
    impossible = False
    constraints = modality.getImpossibles()
    for constraint in constraints:
        matches = True
        for idx, element in enumerate(constraint):
            if element is not ANY and states[idx] != element.value-1: #type: ignore
                matches = False
        impossible |= matches
    return impossible


def fixOpenInputs(module: Module, network: Network, connectorNodes: Dict[Connector, Node]):
    """ Sets a uniform probability for all open inputs

        NEW: take constraints into account, i.e. remove the impossible combinations
    """
    for openInput in module.openInputs():
        node = connectorNodes[openInput]
        table = node.newDistribution().getTable()
        variables = nodeToVariables(node)
        tableIterator = bayesServer.TableIterator(table, variables)
        IntArrayClass = JArray(JInt)
        states = IntArrayClass(len(variables))
        for _ in range(tableIterator.size()):
            tableIterator.getStates(states)
            if isStateImpossible(openInput, states):
                tableIterator.setValue(0.0)
            else:
                tableIterator.setValue(1.0)
            tableIterator.increment()
        table.normalize()
        node.setDistribution(table)
        node.getGroups().add("NotConnected")  

def findWire(plug: InputPlug, module: Module) -> Wire:
    """ Returns the wire that is connected to the given plug"""
    wire = next(wire for wire in module.getConnections(recursive=True) if wire.output == plug)
    assert isinstance(wire, Wire)
    return wire

def findCableTreeNode(wire: Wire, module: Module, cableTreeNodes: Dict[Wire, Node]) -> Node:
    """ Finds the cable tree for a given wire"""
    node = cableTreeNodes.get(wire)
    if node is None:
        joint = findComponent(wire.input, module)
        assert isinstance(joint, WireJoint)
        # find the wire that is connected to the joint input
        inputWire = findWire(joint.inputPlug, module)
        node = findCableTreeNode(inputWire, module, cableTreeNodes)
        cableTreeNodes[wire] = node
    return node

def handleShortToGround(module: Module, network: Network, connectorNodes: Dict[Connector, Node], connectionNodes: Dict[Connection, Node], cableTreeNodes: Dict[Wire, Node]):
    """ Adds links from all wires in a cable tree to the corresponding cable tree node and sets cable tree CPT's"""
    wires = [connection for connection in module.getConnections(recursive = True) if isinstance(connection, Wire)]
    for wire in wires:
        #TODO: optimize for performance
        component = findComponent(wire.input, module)
        if isinstance(component, WireJoint):
            cableTreeNode = findCableTreeNode(wire, module, cableTreeNodes)
            link = bayesServer.Link(connectionNodes[wire], cableTreeNode)
            network.getLinks().add(link)

    # Add CPT to all cable tree nodes, effectively an AND-function assuming the first state is the "good" state
    for cableTreeNode in cableTreeNodes.values():
        table = cableTreeNode.newDistribution().getTable()
        linksIn = cableTreeNode.getLinksIn()
        parentNodes = [link.getFrom() for link in linksIn]
        tableIterator = bayesServer.TableIterator(table, [cableTreeNode]+parentNodes)
        IntArrayClass = JArray(JInt)
        states = IntArrayClass(len(parentNodes)+1)

        # TODO: implement AND-logic less clumsy
        for entry in range(tableIterator.size()):
            tableIterator.getStates(states)
            # this assumes that the link ordering is output first, then all wires. 
            # so: state[0] is the state of the cable tree, state[1] is the state of output, state[2:] are the states of wires
            # Furthermore, it assumes that the ShortToGround is the third state (index 2) of a Wire node
            anyShortToGround = any(state == 2 for state in states[2:])
            if states[0] == 0:
                if states[1] == 0 and not anyShortToGround:
                    tableIterator.setValue(1.0)
                else:
                    tableIterator.setValue(0.0)
            elif states[0] == 1:
                if states[1] != 0 or anyShortToGround:
                    tableIterator.setValue(1.0)
                else:
                    tableIterator.setValue(0.0)
            tableIterator.increment()

        cableTreeNode.setDistribution(table)

def generate(module: Module) -> Tuple[Network, NodeMapping]:
    """ Generates a Bayes net for the given module """

    network = bayesServer.Network(module.name)
    addGroup(network, "Component", "#FFFFFF00")  # yellow
    addGroup(network, "Connector", "#FFCC0000") # yellow
    addGroup(network, "Capability", "#FFBD00F0")  # purple
    #addGroup(network, "Input", "#FF008080")   # light blue
    #addGroup(network, "Output", "#FF4D4DFF")  # blueish
    addGroup(network, "Connection", "#FFFFFF00")  # yellow
    addGroup(network, "Air", "#FF008080") # light blue
    addGroup(network, "Mechanical", "#FFFF00FF") # purple
    addGroup(network, "Material", "#FFFF8000") # orange
    addGroup(network, "Electrical", "#FF00FF00") # green
    addGroup(network, "ComputingResource", "#FF808080") # gray
    addGroup(network, "ErrorMessage", "#FFFFFFFF") #  white
    addGroup(network, "NotConnected", "#FFFF0000") # red
    addGroup(network, "Radiation", "#FFFFAA00") # red/orange
    addGroup(network, "Water", "#FF0000FF") # blue slightly light
    addGroup(network, "Trigger", "#C5C35E") # khaki
    addGroup(network, "Indicator", "#FFFFFFFF") # white
    addGroup(network, "Fuel", "#FFA0522D") # brown
    
    componentNodes = {}
    connectorNodes = {}
    connectionNodes = {}
    cableTreeNodes = {}
    # First generate all modules, then all connections. This ensures that the connection endpoints exist at connection creation time.
    generateModules(module, network, componentNodes, connectorNodes)
    generateConnections(module, network, componentNodes, connectorNodes, connectionNodes, cableTreeNodes)
    generateHealthLinks(module, network, componentNodes, connectorNodes, connectionNodes)
    # At this point, inputs that are not connected do not have a probability table defined.
    # These get assigned a uniform probability
    fixOpenInputs(module, network, connectorNodes)
    # Short to ground failure mode is handled specifically because it has upstream effects
    handleShortToGround(module, network, connectorNodes, connectionNodes, cableTreeNodes)

    for connectorNode in connectorNodes.values():
        connectorNode.getGroups().add("Connector")

    node_mapping = NodeMapping(componentNodes, connectorNodes, connectionNodes)

    return network, node_mapping

def saveNetwork(network: Network, suffix: str = ""):
    """ Saves network to output folder
    
    The network is temporarily named with the suffix so that in Bayes Server
    it is clear which network we are looking at
    """
    underscore_suffix = "_" + suffix if suffix else ""
    originalName = network.getName()
    newName = f"{originalName}{underscore_suffix}"
    network.setName(newName)
    filename = f"output/generated_{newName}.bayes"
    network.save(filename)
    network.setName(originalName)
    print(f"Network saved to {filename}")

def writeNetwork(module: Module):
    network, node_mapping = generate(module)
    saveNetwork(network)

if __name__ == "__main__":
    pass
    

