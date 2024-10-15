import pyAgrum as gum
import re
from deepdiff import DeepDiff
from src.oopnclasses import Node


class ChangeInput:

    def __init__(self, name, target, specs):
        self.name = name
        self.targetcomponent = target
        self.specs = specs
        self.testdecision = None
        self.createTestDecision()
        self.testutility = None
        self.createTestUtility()
        self.internalconnections = []
        self.setInternalConnections()
        self.setTestUtility()


def createTestDecision(self):
    pass
def createTestUtility(self):
    pass
def setInternalConnections(self):
    pass
def setTestUtility(self):
    pass

        