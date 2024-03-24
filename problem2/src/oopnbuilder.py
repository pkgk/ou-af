import pyAgrum as gum
import re
from src.oopnclasses import Component, Connection, Oopn, Node
from src.testobservereplace import ObserveOrReplaceTest


class OopnBuilder():

    def __init__(self, assemblyspecs):
        self.assemblyspecs = assemblyspecs
        self.name = self.assemblyspecs['structure']["name"]
        print("star building system: " + self.name)
        self.oopn = None
        self.components = []
        self.connections = []
        self.tests = []
        self.createComponents()
        print("number of components: " + str(len(self.components)))
        self.createConnections()
        print("number of connections: " + str(len(self.connections)))
        self.createTests()
        print("number of tests: " + str(len(self.tests)))
        self.createOopn()



    def getOopn(self):
        return self.oopn

    # helper to find a specification that matches a given type
    def getTypeSpecs(self, group, ctype):
        for c in self.assemblyspecs[group]:
            if (c["type"] == ctype):
                return c


    def getComponentByName(self, name):
        for c in self.components:
            if (c.getName() == name): return c
        print("Error finding component by name")


    def getConnectionByName(self, name):
        for c in self.connections:
            if (c.getName() == name): return c
        print("Error finding component by name")


    # create components objects
    # loop structure, find specs, create component object
    def createComponents(self):
        # read components from specs
        for k, component in self.assemblyspecs["structure"]["components"].items():
            # read specs for component type
            specs = self.getTypeSpecs("components", component['type'])
            # create new Component object + append to list
            self.components.append(Component(component["name"], specs))

    # create connections objects
    # loop connections in structure, find specs and start/end components,  create connection object
    def createConnections(self):
        try:
            for k, conn in self.assemblyspecs["structure"]["connections"].items():
                connectionspecs = self.getTypeSpecs("connections", conn["type"])
                startcomponent = self.getComponentByName(conn["startComponent"])
                endcomponent = self.getComponentByName(conn["endComponent"])                                         
                self.connections.append(Connection(conn["name"], connectionspecs, startcomponent,endcomponent))
        except KeyError:
            print("KeyError, no connections found")


    # create Test objects
    # loop the testmapping specification, find test specs + targetnode, create testobject
    def createTests(self):
        for k, test in self.assemblyspecs['testmapping'].items():
            for testtype in self.assemblyspecs["tests"]:
                if (test["test"] == testtype["name"]):
                    target = self.getComponentByName(test["target"])
                    if (target == None):
                        target = self.getConnectionByName(test["target"])
                    specs = testtype
                    self.tests.append(ObserveOrReplaceTest(testtype['name'], target, specs))
        
    def createOopn(self):
        self.oopn = Oopn(self.name, self.components, self.connections, self.tests)

    def getOopn(self):
        return self.oopn
