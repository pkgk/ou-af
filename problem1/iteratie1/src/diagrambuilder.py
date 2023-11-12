from deepdiff import DeepDiff
import re
import pyAgrum as gum




#######################################################################
# functions to add nodes to the diagram structure


# loop components that are part of the system
# get the variables representing inputs, outputs, health and add to diagram
# add internal components arcs inputs > output + health > output
def addBNNodesToDiagram(diagram, system):
    for component in system.getComponents():
        print("adding component: " + component.getName())
        variables = component.getVariables()
        for item in variables:
            diagram.addChanceNode(item)
        for connection in component.getInternalConnections():
            diagram.addArc(connection[0], connection[1])


# loop connections that are part of the system
# determine start / end components, add arc between them
# add health to end component
def addComponentConnectionsToDiagram(diagram, system):
    for connection in system.getConnections():
        hid = diagram.addChanceNode(connection.getHealthVariable())
        start = connection.getStartNode()
        end = connection.getEndNode()
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

def setProbabilitiesComponents(diagram, system):

    # loop components, determine nodes
    for component in system.getComponents():
        print("adding cpt for component: " + component.getName())
        health = component.getHealthVarName()
        inputs = component.getInputsVarNames()
        output = component.getOutputsVarName()
        
        # check there are no parents, fill cpt from specs
        if (hasParent(diagram, diagram.idFromName(health)) == False):        
            diagram.cpt(diagram.idFromName(health)).fillWith(component.getHealthPrior())
        for inputnode in inputs:
            if(hasParent(diagram, diagram.idFromName(inputnode)) == False):
                diagram.cpt(diagram.idFromName(inputnode)).fillWith(component.getInputPrior(inputnode))

        # CPT has type Potential and contains tuples (Instantiations) of discrete variables
        # loop in CPT, transform tuple to dict
        # if tuple is in normal behavior table: set P(1), else 0
        for tupleVars in diagram.cpt(diagram.idFromName(output)).loopIn():
            t1 = tupleVars.todict()
            for k, s in component.getCptOutput().items():
                if ('values_changed' not in DeepDiff(s, t1).keys()):
                    diagram.cpt(diagram.idFromName(output)).set(tupleVars, 1)        




# determine probabilities (CPT) for variables of a connection


def setProbabilitiesConnections(diagram, system):

    # loop connections, get endnode and normal behavior table
    for connection in system.getConnections():
        print("adding cpt for connection: " + connection.getName())
        endnode = connection.getEndNode()
        normalbehaviortable = connection.getCptEndComponent()

        # loop cpt and check if state is known as normal behavior
        for tupleVars in diagram.cpt(diagram.idFromName(endnode)).loopIn():
            t1 = tupleVars.todict()
            for k, s in normalbehaviortable.items():
                if ('values_changed' not in DeepDiff(s, t1).keys()):
                    diagram.cpt(diagram.idFromName(endnode)).set(tupleVars, 1)  

        # set cpt for health
        did = diagram.idFromName(connection.getHealthVariable().name())
        diagram.cpt(did).fillWith(connection.getHealthPrior()) 



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
                diagram.cpt(testoutcomeid).set(tupleVars, 1)
#                print("for tuple: " + str(t1) + " set value to: 1")
                break

    


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


def diagramBuilder(diagram, system):
    # add Bayes Network structure to diagram
    addBNNodesToDiagram(diagram, system)

    # add connections
    addComponentConnectionsToDiagram(diagram, system)

    # set prior probabilities for components and connections
    setProbabilitiesComponents(diagram, system)
    setProbabilitiesConnections(diagram, system)

    # add a "replace" decision per component + fill utility
    addReplaceDecisions(diagram, system)
    fillReplaceDecisionUtilities(diagram, system)

    # add tests 
    addTests(diagram, system)

    return diagram