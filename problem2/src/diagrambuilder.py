from deepdiff import DeepDiff
import re
import pyAgrum as gum



# loop components that are part of the system
# get the variables representing inputs, outputs, health and add to diagram
# add internal components arcs inputs > output + health > output
def addBNNodesToDiagram(diagram, oopn):
    for component in oopn.getComponents():
        print("adding component: " + component.getName())
        for node in component.getNodes():
            if (diagram.exists(node.getName()) == True):
               print("node not added, already exists in diagram" + node.getName())
            else:
               diagram.addChanceNode(node.getVariable())
        for connection in component.getInternalConnections():
            diagram.addArc(connection[0], connection[1])


# loop connections that are part of the system
# determine start / end components, add arc between them
# add health to end component
def addComponentConnectionsToDiagram(diagram, oopn):
    for connection in oopn.getConnections():
        start = connection.getStartNode().getName()
        end = connection.getEndNode().getName()
        print("adding connection between: " + start + " and: " + end)
        diagram.addArc(start, end)
        if (diagram.exists(connection.getHealthNode().getName()) == True):
            print("node not added, already exists in diagram" + connection.getHealthNode().getName())
            diagram.addArc(diagram.idFromName(connection.getHealthNode().getName()), diagram.idFromName(end))
        else:
            hid = diagram.addChanceNode(connection.getHealthNode().getVariable())
            diagram.addArc(hid, diagram.idFromName(end))


# determine probabilities (CPT) for variables of a component

def hasParent(diagram, diagId):
    for a in diagram.arcs():
        if (a[1] == diagId): return True
    return False          

def setProbabilitiesComponents(diagram, oopn):

    # loop components, determine nodes
    for component in oopn.getComponents():
        print("adding cpt for component: " + component.getName())
        for node in component.getNodes():
            potentialoopn = node.getPrior()
            potentialdiagram =  diagram.cpt(diagram.idFromName(node.getName())) 
            if (potentialoopn.names == potentialdiagram.names):
                potentialdiagram.fillWith((potentialoopn))
            else:
                print("potential node not identical to potential in diagram:" + str(node.getName()))
                print("diagram: " + str(potentialdiagram.names) + " oopn: " + str(potentialoopn.names))




# determine probabilities (CPT) for variables of a connection
def setProbabilitiesConnections(diagram, system):

    # loop connections, get endnode and normal behavior table
    for connection in system.getConnections():
        print("adding cpt for connection: " + connection.getName())

        # set cpt for health
        healthname = connection.getHealthNode().getName()
        potentialdiagram = diagram.cpt(diagram.idFromName(healthname))
        potentialoopn = connection.getHealthNode().getPrior()
        if (potentialoopn.names == potentialdiagram.names):
            potentialdiagram.fillWith((potentialoopn))
        else:
            print("potential node not identical to potential in diagram:" + str(healthname))
            print("diagram: " + str(potentialdiagram.names) + " oopn: " + str(potentialoopn.names))



def transferPotential(diagram, node):
    potentialoopn = node.getPrior()

    # cpt or utility?
    if (node.getType() == "Utility"):
        potentialdiagram =  diagram.utility(diagram.idFromName(node.getName())) 
    if (node.getType() == "TestOutcome"):
        potentialdiagram =  diagram.cpt(diagram.idFromName(node.getName())) 

    if (potentialoopn.names == potentialdiagram.names):
        potentialdiagram.fillWith((potentialoopn))
    else:
        print("potential node not identical to potential in diagram:" + str(node.getName()))
        print("diagram: " + str(potentialdiagram.names) + " oopn: " + str(potentialoopn.names))



def addTests(diagram, oopn):
    for test in oopn.getTests():
        print("adding test: " + test.getName())
        for node in test.getNodes():
            print("adding node: " + node.getName())
            if (node.getType() == "Decision"):
                diagram.addDecisionNode(node.getVariable())
            if (node.getType() == "Utility"):
                diagram.addUtilityNode(node.getVariable())
            if (node.getType() == "TestOutcome"):
                diagram.addChanceNode(node.getVariable())
        for conn in test.getInternalConnections():
            print("add edge from: " + conn[0] + " to: " + conn[1])
            diagram.addArc(conn[0], conn[1])


    # loop testnodes, add cpt or utilityy
    for test in oopn.getTests():
        for node in test.getNodes():
            if (node.getType() == "Utility"):
                print("adding utility to: " + node.getName())
                transferPotential(diagram, node)
            if (node.getType() == "TestOutcome"):
                print("adding cpt to: " + node.getName())
                transferPotential(diagram, node)


# method to add a sytemhealth variable to the diagram
def addSystemHealth(diagram, oopn):
    sh = oopn.getSystemHealth()
    print("adding systemHealth variable: ")
    diagram.addChanceNode(sh.getNode().getVariable())

    print("adding systemhealth connections")
    for healthnode in sh.getHealthNodes():
        diagram.addArc(healthnode.getName(), sh.getName())



#######################################################################
# MAIN builder 


def diagramBuilder(diagram, oopn):
    # add Bayes Network structure to diagram
    addBNNodesToDiagram(diagram, oopn)

    # add connections
    addComponentConnectionsToDiagram(diagram, oopn)

    # set prior probabilities for components and connections
    setProbabilitiesComponents(diagram, oopn)
    setProbabilitiesConnections(diagram, oopn)

    # voeg eventueel systemhealth toe
    if (oopn.getSystemHealth() != None):
        addSystemHealth(diagram, oopn)

    # add ObserveOrReplacetests
    addTests(diagram, oopn)

    return diagram