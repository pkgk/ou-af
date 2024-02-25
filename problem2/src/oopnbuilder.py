import pyAgrum as gum
import re
from src.oopnclasses import Component, Connection, ObserveTest, Assembly


class OopnBuilder():

    def __init__(self, assemblyspecs):
        self.assemblyspecs = assemblyspecs
        self.name = self.assemblyspecs['structure']["name"]
        self.oopn = None
        print("building system: " + self.name)
        self.components = []
        self.connections = []
        self.tests = []
        self.createComponents()
        print("number of components: " + str(len(self.components)))
        self.createConnections()
        print("number of connections: " + str(len(self.connections)))
        self.createTests()
        print("number of tests: " + str(len(self.tests)))
        self.createAssembly()



    def getOopn(self):
        return self.oopn

    # helper to find a specification that matches a given type
    def getTypeSpecs(self, group, ctype):
        for c in self.assemblyspecs[group]:
            if (c["type"] == ctype):
                return c

    # helper to find a specific component by name in list of components
    def findComponent(self, requestedcomponent):
        for component in self.components:
            if (component.getName() == requestedcomponent):
                return component

    # helper to determine start / end nodes based on list of existing components and connection specs
    def determineConnectionStartEndNodes(self, connectionspecs, connection):
        # determine startComponent: variablename
        startcomponentobject = self.findComponent(connection["startComponent"])
        endcomponentobject = self.findComponent(connection["endComponent"])
        for label in startcomponentobject.getVariables():
            if(re.search(connectionspecs["start"], label.name())):
                startname = label.name()
        for label in endcomponentobject.getVariables():
            if(re.search(connectionspecs["end"], label.name())):
                endname = label.name()
        return (startname, endname)

    
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
                startendnames = self.determineConnectionStartEndNodes(connectionspecs, conn)
                self.connections.append(Connection(conn["name"], connectionspecs,startendnames[0],startendnames[1]))
        except KeyError:
            print("KeyError, no connections found")


    # create Test objects
    # loop the testmapping specification, find test specs + targetnode, create testobject
    def createTests(self):
        for k, test in self.assemblyspecs['testmapping'].items():
            for testtype in self.assemblyspecs["tests"]:
                if (test["test"] == testtype["name"]):
                    specs = testtype
                    self.tests.append(ObserveTest(testtype['name'], test["target"], specs))
        
    def createAssembly(self):
        self.oopn = Assembly(self.name, self.components, self.connections, self.tests)

