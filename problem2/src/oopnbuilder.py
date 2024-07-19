import pyAgrum as gum
import re
from src.oopnclasses import Component, Connection, Oopn, Node, SystemHealth
from src.testobservereplace import ObserveOrReplaceTest
from src.testchangeinput import ChangeInputTest

# class generates objects for components, connections and tests to form a object oriented probebility network
# inputs: specifications of components, connections and test stored as dictionaries in /specs directory

class OopnBuilder():

    # objects for components, connections and test are generated and stored when OopnBuilder object is created
    def __init__(self, assemblyspecs):
        self.assemblyspecs = assemblyspecs
        self.name = self.assemblyspecs['structure']["name"]
        print("start building system: " + self.name)

        # variable list to store components, connectinos and tests
        self.components = []
        self.connections = []
        self.tests = []
        self.systemhealth = None

        self.oopn = Oopn(self.name, self.components, self.connections, self.tests, self.systemhealth)
        # create components, connections and tests
        self.createComponents()
        print("number of components: " + str(len(self.components)))
        self.createConnections()
        print("number of connections: " + str(len(self.connections)))
        if (self.assemblyspecs["structure"]["systemhealth"] == "yes"):
            self.oopn.setSystemHealth(self.createSystemHealth())
            print("added systemHealth")
        self.createTests()
        print("number of tests: " + str(len(self.tests)))


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

    def getConnections(self):
        return self.connections



    # create components objects
    # loop structure, find specs, create component object
    def createComponents(self):
        # read components from specs
        for k, component in self.assemblyspecs["structure"]["components"].items():
            # read specs for component type
            specs = self.getTypeSpecs("components", component['type'])
            # create new Component object + append to list
            self.components.append(Component(component["name"], specs, []))

    # create connections objects
    # loop connections in structure, find specs and start/end components,  create connection object
    def createConnections(self):
        try:
            for k, conn in self.assemblyspecs["structure"]["connections"].items():
                connectionspecs = self.getTypeSpecs("connections", conn["type"])
                startcomponent = self.getComponentByName(conn["startComponent"])
                endcomponent = self.getComponentByName(conn["endComponent"])                                         
                self.connections.append(Connection(conn["name"], connectionspecs, startcomponent,endcomponent, None))
        except KeyError:
            print("KeyError, no connections found")


    # add observeorreplacetest 
    def createObserveOrReplaceTest(self, target, name, specs):
        # find targetcomponent
        targetcomponent = self.getComponentByName(target)
        # if target is no component then search connections
        if (targetcomponent == None):
            targetcomponent = self.getConnectionByName(target)
        self.tests.append(ObserveOrReplaceTest(name, targetcomponent, specs))


    # add changeinputtest
    def createChangeInputTest(self, target, name, specs ):
        targetcomponent = self.getComponentByName(target)
        if (targetcomponent == None):
            targetcomonent = self.getConnectionByName(target)
        start = specs["componentChain"]["start"]
        end = specs["componentChain"]["end"]
        # duplicate the nodes of the chain given in the specs
        self.oopn.copyPathType2Test(start, end)
        self.tests.append(ChangeInputTest(name, targetcomponent, specs, self.oopn))


    # create Test objects
    # loop the testmapping specification, find test specs + targetnode, create testobject
    def createTests(self):
        # loop tests defined in mapping
        for k, test in self.assemblyspecs['testmapping'].items():
            testtype = test["test"]
            target = test["target"]
            # loop available specs for tests until the right spec for test from mapping is found
            for testspec in self.assemblyspecs["tests"]:
                if (testtype == testspec["name"]):
                    if (testtype == "ObserveOrReplaceTest"):
                        self.createObserveOrReplaceTest(target, testtype, testspec)
                    if (testtype == "ChangeInputTest"):
                        self.createChangeInputTest(target, testtype, testspec)


    def getHealthNodes(self):
        healthnodes = []
        for comp in self.components:
            healthnode = comp.getHealthNode()
            healthnodes.append(healthnode)
        for conn in self.connections:
            healthnode = conn.getHealthNode()
            healthnodes.append(healthnode)
        return healthnodes
    
    def createSystemHealth(self):
        return SystemHealth("systemhealth", self.getHealthNodes())




    # create Oopn object to contain all compoonents, connects an tests and return it    
    def getOopn(self):
        return self.oopn
