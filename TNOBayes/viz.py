from concepts import *
from connectors import *  # for coloring
from connections import Ability  # special treatment

import pyyed
import os

#from cytoscape import writeCytoscape

class Colors():
    # palette https://coolors.co/f94144-f3722c-f8961e-f9c74f-90be6d-43aa8b-577590-8197ab
    Red = "#F94144"
    OrangeRed = "#F3722C"
    Orange = "#F8961E"
    Yellow = "#F9C74F"
    Lime = "#90BE6D"
    Green = "#43AA8B"
    Khaki = "#c5c35e"
    Blue = "#7070FF"
    BlueGray = "#577590"
    DarkGray = "#91a3b6"
    LightGray = "#C2CCD6"
    Purple = "#3e23d1"
    LightBlue = "#6B6BFF"
    Black = "#000000"
    White = "#e7ebef"
    Brown = "#A0522D"

def healthNodeName(unreliable:Unreliable):
    return "Health " + unreliable.name

def healthNodeLabel(component:Component):
    return component.shortName

def stateNodeName(state):
    return "State " + state.name

def stateNodeLabel(state):
    return state.shortName

def connectorColor(connector:Connector):
    if isinstance(connector, Power):
        return Colors.Green
    elif isinstance(connector, Air):
        return Colors.Blue
    elif isinstance(connector, Movement):
        return Colors.OrangeRed
    elif isinstance(connector, Sheet):
        return Colors.Lime
    elif isinstance(connector, Heat):
        return Colors.Red
    elif isinstance(connector, (Water, Moisture)):
        return Colors.Blue
    elif isinstance(connector, Fuel):
        return Colors.Brown
    try:
        return connector.color  #type: ignore this is an optional attribute
    except:
        return Colors.Khaki

def addComponent(g, component:Component):
    nodeName = healthNodeName(component)
    inputs =  [inp for inp  in filter(lambda inp: (not smallGraph) or inp.alwaysVisible(), component.getInputs())]
    outputs = [outp for outp in filter(lambda outp: (not smallGraph) or outp.alwaysVisible(), component.getOutputs())]

    if len(inputs)==0 and  len(outputs)==0:
        g.add_node(nodeName, label=healthNodeLabel(component), shape="roundrectangle", shape_fill=Colors.Yellow, node_type=type(component).__name__)
    else:
        group = g.add_group(component.name, label=component.shortName, fill=Colors.DarkGray)
        group.add_node(nodeName, label=healthNodeLabel(component), shape="roundrectangle", shape_fill=Colors.Yellow, node_type=type(component).__name__)
        for input in inputs:
            group.add_node(input.name, label=input.shortName, shape="ellipse", shape_fill=connectorColor(input),node_type=type(input).__name__)
            group.parent_graph.add_edge(input.name, nodeName, line_type="dashed")
        for output in outputs:
            group.add_node(output.name, label=output.shortName, shape="octagon", shape_fill=connectorColor(output),node_type=type(output).__name__)
            group.parent_graph.add_edge(nodeName, output.name, line_type="dashed")

def addCapability(g, capability:Capability):
    g.add_node(capability.name, label=capability.shortName, shape="roundrectangle", shape_fill=Colors.White)

def connectionLabel(connection):
    """ Connection labels show the "type", e.g. wire, pipe, ...
    """
    return connection.name.split(' ',maxsplit=1)[0] # take first word

def addState(g, state:State):
    nodeName = stateNodeName(state)
    if smallGraph:
        g.add_node(stateNodeName(state), label=stateNodeLabel(state), shape="parallelogram", shape_fill=Colors.Yellow)
    else:
        group = g.add_group(state.name, label=state.shortName, fill=Colors.DarkGray)
        group.add_node(nodeName, label=stateNodeLabel(state), shape="parallelogram", shape_fill=Colors.Yellow)
        for input in state.getInputs():
            group.add_node(input.name, label=input.shortName, shape="ellipse", shape_fill=connectorColor(input))
            group.parent_graph.add_edge(input.name, nodeName, line_type="dashed")
        for output in state.getOutputs():
            group.add_node(output.name, label=output.shortName, shape="octagon", shape_fill=connectorColor(output))
            group.parent_graph.add_edge(nodeName, output.name, line_type="dashed")

def addModules(g, module:Module):
    #print("Adding {}".format(module.name))
    if isinstance(module, Assembly):
        group = g.add_group(module.name, label=module.shortName, fill=Colors.LightGray)
        for connection in module.getConnections(recursive=False):  #TODO: make it smarter
            if allConnectionNodes or anyCapabilityUsingThisConnection(module, connection):
                group.add_node(healthNodeName(connection), label=connectionLabel(connection), shape="ellipse", shape_fill=connectorColor(connection.input))
        for dummyConnection in module.getDummyConnections(recursive=False):
            group.add_node(healthNodeName(dummyConnection), label=connectionLabel(dummyConnection), shape="ellipse", shape_fill=connectorColor(dummyConnection.input))
        for unusedConnection in module.getUnusedConnections(recursive=False):
            group.add_node(healthNodeName(unusedConnection), label=connectionLabel(unusedConnection), shape="ellipse", shape_fill=connectorColor(unusedConnection.input))
        for m in module.getModules():
            addModules(group, m)
    elif isinstance(module, Component):
        addComponent(g, module)
    elif isinstance(module, Capability):
        addCapability(g, module)
    elif isinstance(module, State):
        addState(g, module)
    else:
        assert False, f"Unsupported module type {type(module)}"        

def anyCapabilityUsingThisConnection(module:Module, connection:Connection):
    """ Checks if there is a capability that uses this connection as unreliable input """
    capabilities = list(module.getCapabilities(recursive=True))
    isUsed = any(inp for c in capabilities for inp in c.inputs if inp[0] == connection)
    return isUsed

def findComponent(module:Module, connector:Connector) -> Component:
    component = connector.parent
    assert isinstance(component, Component)
    return component

def addConnections(g, module:Module):
    for connection in module.getConnections(recursive=True):
        if smallGraph:
            fromComponent = findComponent(module, connection.input)
            toComponent = findComponent(module, connection.output)
            fromElementName = healthNodeName(fromComponent)
            toElementName = healthNodeName(toComponent)
        else:
            fromElementName = connection.input.name
            toElementName = connection.output.name
        
        if isinstance(connection, Ability):
            capability = connection.input # capability is its own output connector
            g.add_edge(capability.name, toElementName, description=connection.getName())
        else:
            # Only add node when necessary (see if this connection plays a role in an ability)
            if allConnectionNodes or anyCapabilityUsingThisConnection(module, connection):
                g.add_edge(fromElementName, healthNodeName(connection), width="2.0", color=connectorColor(connection.input), description=connection.getName())
                g.add_edge(healthNodeName(connection), toElementName, width="2.0", color=connectorColor(connection.input), description=connection.getName())
            else:
                g.add_edge(fromElementName, toElementName, color=connectorColor(connection.input), width="2.0", description=connection.getName())

def addDummyConnections(g, module:Module):
    for dummyConnection in module.getDummyConnections(recursive=True):
        if smallGraph:
            componentFrom = findComponent(module, dummyConnection.input)
            componentTo = findComponent(module, dummyConnection.output)
            fromElementName = healthNodeName(componentFrom)
            toElementName = healthNodeName(componentTo)
        else:
            fromElementName = dummyConnection.input.name
            toElementName = dummyConnection.output.name

        g.add_edge(fromElementName, healthNodeName(dummyConnection), width="2.0", line_type="dotted", color=connectorColor(dummyConnection.input), description=dummyConnection.getName())
        g.add_edge(healthNodeName(dummyConnection), toElementName, width="2.0", line_type="dotted", color=connectorColor(dummyConnection.input), description=dummyConnection.getName())

def addHealthLinks(g, module:Module):
    for component in module.getCapabilities(recursive=True):
        for unreliable, _ in component.inputs:
            if isinstance(unreliable, Capability):
                g.add_edge(unreliable.name, component.name, color=Colors.Black)
            else:
                g.add_edge(healthNodeName(unreliable), component.name, color=Colors.Black)

def populateGraph(g, module:Module):
    addModules(g, module)
    addConnections(g, module)
    addDummyConnections(g, module)
    addHealthLinks(g, module)

def writeGraph(module: Module, includeConnectors:bool=True, alwaysShowConnectionNodes:bool=False):
    global smallGraph
    global allConnectionNodes
    smallGraph = not includeConnectors
    allConnectionNodes = alwaysShowConnectionNodes
    g = pyyed.Graph("directed", module.name + "_")
    populateGraph(g, module)
    if smallGraph:
        filename = f"output{os.path.sep}{module.name} small"
    else:
        filename = f"output{os.path.sep}{module.name}"
    g.write_graph(filename + ".graphml")
    print(f"GraphML written to {filename}.graphml")
    #writeCytoscape(g, filename+".json")
    #print(f"Cytoscape JSON written to {filename}.json")

smallGraph = False
allConnectionNodes = False

if __name__ == "__main__": 
    pass