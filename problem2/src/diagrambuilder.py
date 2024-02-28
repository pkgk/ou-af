from deepdiff import DeepDiff
import re
import pyAgrum as gum




#######################################################################
# functions to add nodes to the diagram structure


# loop components that are part of the system
# get the variables representing inputs, outputs, health and add to diagram
# add internal components arcs inputs > output + health > output
def addBNNodesToDiagram(diagram, oopn):
    for component in oopn.getComponents():
        print("adding component: " + component.getName())
        for node in component.getNodes():
            diagram.addChanceNode(node.getVariable())
        for connection in component.getInternalConnections():
            diagram.addArc(connection[0], connection[1])


# loop connections that are part of the system
# determine start / end components, add arc between them
# add health to end component
def addComponentConnectionsToDiagram(diagram, oopn):
    for connection in oopn.getConnections():
        hid = diagram.addChanceNode(connection.getHealthNode().getVariable())
        start = connection.getStartNode().getName()
        end = connection.getEndNode().getName()
        print("adding connection between: " + start + " and: " + end)
        diagram.addArc(start, end)
        diagram.addArc(hid, diagram.idFromName(end))





#######################################################################
# functions to determine prior probability



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
                print("potential not identical:" + str(node.getName()))
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
            print("potential not identical:" + str(healthname))
            print("diagram: " + str(potentialdiagram.names) + " oopn: " + str(potentialoopn.names))




#######################################################################
# functions to add replace decision to diagram


# add decision to replace component for every component that is part of the structure
def addReplaceDecisions(diagram, system):

    for component in system.getComponents():
        print("adding Replace decision for component: " + component.getName())
        healthnodename = component.getHealthVarName()
        decision = component.getReplaceDecision()
        diagram.addDecisionNode(decision["decision"])
        diagram.addUtilityNode(decision["utility"])
        for arc in decision["arcs"]:
            diagram.addArc(arc[0], arc[1])



# given costs calculate utility per row in utility table

def calculateReplaceUtility(diagram, diagramNodeIndex, utilitytable, replacementcosts, incorrectreplacementcosts, failuretorepaircosts):
    for t in utilitytable.loopIn():
        utilitycosts = 0
        healthy = None
        replace = None
        utilityrow = t.todict()

        # loop in utility table, determine state for health or repair
        for k, row in utilityrow.items():
            if(re.search("health", k)):
                if (row == "ok"): healthy = True
                else:             healthy = False
            elif(re.search("Replace", k)):
                if (row == "yes"): replace = True
                else:              replace = False
    
        if (healthy != None or replace != None ):
            if (healthy and replace): 
                utilitycosts = replacementcosts + incorrectreplacementcosts
            elif(not healthy and replace):
                utilitycosts = replacementcosts 
            elif(not healthy and not replace):
                utilitycosts = failuretorepaircosts
        diagram.utility(diagramNodeIndex)[utilityrow] = utilitycosts





# loop components, get costs, calculate utility
def fillReplaceDecisionUtilities(diagram, system):
    
    for component in system.getComponents():
        print("adding Replace utility for component: " + component.getName())

        # get the decision and costs
        decision = component.getReplaceDecision()
        replacementcost = decision["replacementcosts"]
        incorrectreplacementcosts = decision["incorrectreplacementcosts"]
        failuretorepaircosts = decision["failuretorepaircosts"]

        # calculate utility based on costs and paste into utility table
        did = diagram.idFromName(decision["utility"].name())
        calculateReplaceUtility(diagram, did, diagram.utility(did), replacementcost, incorrectreplacementcosts, failuretorepaircosts)




#######################################################################
# functions to add tests 

# given costs calculate utility per row in utility table

def calculateTestUtility(diagram, diagramNodeIndex, testcosts):
    for t in diagram.utility(diagramNodeIndex).loopIn():
        utilityrow = t.todict()
        utility = 0

        # loop in utility table, determine state for health or repair
        for k, row in utilityrow.items():
            if(re.search("Decision", k)):
                if (row == "yes"): 
                    utility = testcosts
    
        diagram.utility(diagramNodeIndex)[utilityrow] = utility







def addTestCPTs(diagram, testoutcomeid, testobject):
    cpttable = testobject.getTestOutcomeCpt()
#    print(cpttable)

    # loop cpt and check states
    for tupleVars in diagram.cpt(testoutcomeid).loopIn():
        t1 = tupleVars.todict()
#        print("")
#        print("diagram cpt : " + str(t1))
        for k, s in cpttable.items():
#            print("specs normaal tabel entry: " + str(s))
#            print("deepdiff voor voorgaande: " + str(DeepDiff(s, t1)))
            if ('values_changed' not in DeepDiff(s, t1).keys()):
                diagram.cpt(testoutcomeid).set(tupleVars, 0.9999)
#                print("for tuple: " + str(t1) + " set value to: 1")
                break
            else:
                diagram.cpt(testoutcomeid).set(tupleVars, 0.0001)

    


def addTests(diagram, system):
    
    for test in system.getTests():
        print("adding test: " + test.getName() + " to component: " + test.getTarget())
        
        # names for nodes
        decisionNodeLabel = "Decision" + test.getName() + test.getTarget()
        utilityNodeLabel = "Utility" + test.getName() + test.getTarget()
        testoutcomeNodeLabel = "TestOutcome" + test.getName() + test.getTarget()
        testoutcomeToReplaceDecision = test.getTestoutcometargetNode()

        # add Node for Decision
        decisionNodeId = diagram.addDecisionNode(gum.LabelizedVariable(decisionNodeLabel,decisionNodeLabel,test.getDecisionValues()))

        # add Node for utility + arc D > U
        utilityNodeId = diagram.addUtilityNode(gum.LabelizedVariable(utilityNodeLabel, utilityNodeLabel, 1))
        diagram.addArc(decisionNodeId, utilityNodeId)
        
        # add Node for test outcome + arc D + Health > TO
        testoutcomeNodeId = diagram.addChanceNode(gum.LabelizedVariable(testoutcomeNodeLabel, testoutcomeNodeLabel, test.getTestOutcomeValues()))
        diagram.addArc(decisionNodeId, testoutcomeNodeId)
    
        # add arc from health > testoutcome
        diagram.addArc(diagram.idFromName("health" + test.getTarget()), testoutcomeNodeId)
        
        # add arc from testoutcome to decision to replace
        if (testoutcomeToReplaceDecision is not None):
            diagram.addArc(diagram.idFromName(testoutcomeNodeLabel), diagram.idFromName(testoutcomeToReplaceDecision))
        
        addTestCPTs(diagram, testoutcomeNodeId, test)
        
        testcost = test.getTestCosts()       
        # calculate test decision utility based on costs and paste into utility table
        calculateTestUtility(diagram, utilityNodeId, testcost)





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

    # add a "replace" decision per component + fill utility
#    addReplaceDecisions(diagram, system)
#    fillReplaceDecisionUtilities(diagram, system)

    # add tests 
#    addTests(diagram, system)

    return diagram