import pyAgrum as gum
import re
from deepdiff import DeepDiff
from src.oopnclasses import Node



# class ObserveOrReplaceTest models an observation test together with a replace decision
# test is defined by
# name 
# target component + attachment to healthnode
# Test decision + utilty
# TestOutcome
# Replace decision + utility

class ObserveOrReplaceTest:
    def __init__(self, name, target, specs):
        self.name = name
        self.targetcomponent = target
        self.specs = specs
        self.testdecision = None
        self.createTestDecision()
        self.testutility = None
        self.createTestUtility()
        self.testoutcome = None
        self.createTestOutcome()
        self.replacedecision = None
        self.createReplaceDecision()
        self.replaceutility = None
        self.createReplaceUtility()
        self.internalconnections = []
        self.setInternalConnections()
        self.setTestUtility()
        self.setTestOutcomeCpt()
        self.setReplaceUtility()

    def getName(self):
        return self.name
    def getTarget(self):
        return self.targetcomponent
    def getTestDecision(self):
        return self.testdecision
    def getTestUtility(self):
        return self.testutility
    def getTestOutcome(self):
        return self.testoutcome
    def getReplaceDecision(self):
        return self.replacedecision
    def getReplaceUtility(self):
        return self.replaceutility
    def getNodes(self):
        return [self.testdecision, self.testutility, self.testoutcome, self.replacedecision, self.replaceutility]
    def getInternalConnections(self):
        return self.internalconnections
    

    def createTestDecision(self):
        # get values test decision
        decvalues = self.specs["Testdecision"]["values"]
        # create labelizedvariable + node
        label = "Decision" + self.name + self.targetcomponent.getName()
        self.testdecision = Node(label, "Decision", gum.LabelizedVariable(label, label, decvalues))

    def createTestUtility(self):
        # get costs of test
        testcosts = self.specs["TestUtility"]["testcosts"]
        # create utility variable + node
        label = "Utility" + self.name + self.targetcomponent.getName()
        self.testutility = Node(label, "Utility", gum.LabelizedVariable(label, label, 1))

    def createTestOutcome(self):
        # get costs of test
        tovalues = self.specs["TestOutcome"]["testoutcomevalues"]
        # create utility variable + node
        label = "TestOutcome" + self.name + self.targetcomponent.getName()
        self.testoutcome = Node(label, "TestOutcome", gum.LabelizedVariable(label, label, tovalues))

    def createReplaceDecision(self):
        rvalues = self.specs["Replacedecision"]["values"]
        label = "Decision" + "Replace" + self.targetcomponent.getName()
        self.replacedecision = Node(label, "Decision", gum.LabelizedVariable(label, label, rvalues))

    def createReplaceUtility(self):
        # get costs of replacements
        replacementcosts = self.specs["Replacedecision"]["replacementcosts"]
        incorrectreplacementcostscosts = self.specs["Replacedecision"]["incorrectreplacementcosts"]
        failuretorepaircostscosts = self.specs["Replacedecision"]["failuretorepaircosts"]
        # create utility variable + node
        label = "Utility" + "Replace" + self.targetcomponent.getName()
        self.replaceutility = Node(label, "Utility", gum.LabelizedVariable(label, label, 1))

    def setInternalConnections(self):
        self.internalconnections.append( (self.testdecision.getName(), self.testutility.getName() ))
        self.internalconnections.append( (self.testdecision.getName(), self.testoutcome.getName() ))
        self.internalconnections.append( (self.testoutcome.getName(), self.replacedecision.getName() ))
        self.internalconnections.append( (self.replacedecision.getName(), self.replaceutility.getName())    )
        self.internalconnections.append( (self.targetcomponent.getHealthNode().getName(), self.testoutcome.getName() ))
        self.internalconnections.append( (self.targetcomponent.getHealthNode().getName(), self.replaceutility.getName() ))



    # transforms the readable behavior table from specs to a format for use
    # during creation of a potential
    def transformBehaviorTable(self):
        cptDict = {}
        for k, v in self.specs['TestOutcome']['testoutcomecpt'].items():
            var = k + self.targetcomponent.getName()
            count = 0
            for e in v:
                if count in cptDict:
                    d = cptDict[count]
                    d[var] = e
                else:
                    cptDict[count] = {var: e}
                count = count + 1
        return cptDict


    def setTestOutcomeCpt(self):
        # first create the potential with all the probabilities
        # P(X | Y, Z) X should be first variable when creating potential
        # P(TestOutcome | health, DecisionTest)

        #add X 
        p = gum.Potential().add(self.testoutcome.getVariable())

        # number of labels for X is relevant for determinining probability later on
        xnumberoflabels = len(self.testoutcome.getVariable().labels())

        p.add(self.testdecision.getVariable())
        p.add(self.targetcomponent.getHealthNode().getVariable())

        # secondly get behavior table
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
        self.testoutcome.setPrior(p)


    def setTestUtility(self):
        # utility table is a potential so create and add variable
        pot = gum.Potential().add(self.testutility.getVariable())
        i = gum.Instantiation().add(self.testutility.getVariable())
        pot.add(self.testdecision.getVariable())
        i.add(self.testdecision.getVariable())
        i.chgVal(self.testdecision.getVariable(), 0)   # 0 = "yes"
        p = self.specs["TestUtility"]["testcosts"]
        pot.set(i, p)
        self.testutility.setPrior(pot) 




    # diagram > node
    # diagranNodeIndex > node
    # utilitytable > potential
    def calculateReplaceUtility(self, potential, replacementcosts, incorrectreplacementcosts, failuretorepaircosts):
        for t in potential.loopIn():
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
            potential.set(t, utilitycosts)
        return potential

    def setReplaceUtility(self):
        pot = gum.Potential().add(self.replaceutility.getVariable())
        pot.add(self.replacedecision.getVariable())
        pot.add(self.targetcomponent.getHealthNode().getVariable())
        replacementcosts = self.specs["Replacedecision"]["replacementcosts"]
        incorrectreplacementcosts = self.specs["Replacedecision"]["incorrectreplacementcosts"]
        failuretorepaircosts = self.specs["Replacedecision"]["failuretorepaircosts"]
        self.replaceutility.setPrior(self.calculateReplaceUtility(pot, replacementcosts, incorrectreplacementcosts,failuretorepaircosts ))





