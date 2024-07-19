import pyAgrum as gum
import re
from deepdiff import DeepDiff
from src.oopnclasses import Node



# class ChangeInputTest models a "type II"  test which changes input for parts of the system
class ChangeInputTest:
    def __init__(self, name, target,specs, oopn):
        self.duplicatedNodeExtension = "copy"
        self.oopn = oopn
        self.name = name                      # name of the test, type:str
        self.targetcomponent = target         # system component to connect to, type:Component
        self.specs = specs                    # specs of the test, type:dict
        self.testdecision = None              # decision to start test, type:Node
        self.utilityparents = []             # needed for filling in utility table
        self.createTestDecision()           
        self.testutility = None               # utility to steer decision, type:Node
        self.createTestUtility()
        self.internalconnections = []         # list of connections, type:list of tuples
        self.setInternalConnections()
        self.setTestUtility()

    def getName(self):
        return self.name
    def getTarget(self):
        return self.targetcomponent
    def getTestDecision(self):
        return self.testdecision
    def getTestUtility(self):
        return self.testutility
    def getNodes(self):
        return [self.testdecision, self.testutility]
    def getInternalConnections(self):
        return self.internalconnections
    
    # create testdecision Node from specs
    def createTestDecision(self):
        # get values test decision
        decvalues = self.specs["Testdecision"]["values"]
        # create labelizedvariable + node
        label = "Decision" + self.name + self.targetcomponent.getName()
        self.testdecision = Node(label, "Decision", gum.LabelizedVariable(label, label, decvalues))

    # create testutility Node from specs
    def createTestUtility(self):
        # get costs of test
        testcosts = self.specs["TestUtility"]["testcosts"]
        # create utility variable + node
        label = "Utility" + self.name + self.targetcomponent.getName()
        self.testutility = Node(label, "Utility", gum.LabelizedVariable(label, label, 1))


    # create internal connections + interface with Output Node of target component
    def setInternalConnections(self):
        duplicatedInputNode = self.specs["componentChain"]["start"] 
        # decision > duplicated inputnode
        self.internalconnections.append( (self.testdecision.getName(), duplicatedInputNode + self.duplicatedNodeExtension  ))
        # system outputnode > decision
        self.internalconnections.append( (self.targetcomponent.getOutputNode().getName(), self.testdecision.getName() ))
        # duplicated inputnode > utility
        self.internalconnections.append( (duplicatedInputNode + self.duplicatedNodeExtension , self.testutility.getName()))
        self.utilityparents.append(duplicatedInputNode + self.duplicatedNodeExtension)
        # systemhealth > utility
        self.internalconnections.append( ("systemhealth", self.testutility.getName()))
        self.utilityparents.append("systemhealth" )
        # system input > utility
        self.internalconnections.append( ( duplicatedInputNode, self.testutility.getName()   ))
        self.utilityparents.append(duplicatedInputNode)


    # set test utility based on costs defined in specs
    def setTestUtility(self):
#        # utility table is a potential so create and add variable
        pot = gum.Potential().add(self.testutility.getVariable())
        i = gum.Instantiation().add(self.testutility.getVariable())

        for e in self.utilityparents:
            vars = []
            if e == "systemhealth":
                vars.append(self.oopn.getSystemHealth().getNode().getVariable())
            else:
                node = self.oopn.findNodeFromName(e)
                if node != None:
                    vars.append(node.getVariable())
        for v in vars:
            pot.add(v )
            i.add(v)

#        i.chgVal(al, 0)   # 0 = "yes"
#        p = self.specs["TestUtility"]["testcosts"]
#        pot.set(i, p)
        self.testutility.setPrior(pot) 


