import pytest
import pyAgrum
from src.oopnclasses import Component, Connection, Oopn, ObserveOrReplaceTest
from src.oopnbuilder import OopnBuilder
import specs.components as componentspecs
import specs.connections as connectionspecs
import specs.tests as testspecs
import specs.assemblies as assemblyspecs



### 
def test_oopnbuilder():
    # gather specs for a system
    # system = light + replacedecision + test
    components = [componentspecs.light, componentspecs.switch]
    connections = [connectionspecs.wire, connectionspecs.wire2]
    tests = [testspecs.observeorreplacetest]
    assembly = {
        "components"  : components,
        "connections" : connections,
        "structure"   : assemblyspecs.structure1,   #light + switch + wire
        "tests"       : tests,
        "testmapping" : testspecs.testmapping1
    }

    oopnbuilder = OopnBuilder(assembly)
    oopn = oopnbuilder.getOopn()
    assert type(oopn) == Oopn
    assert oopn.getName() == "structure1"
    assert len(oopn.getComponents()) == 2
    assert len(oopn.getConnections()) == 1
    assert len(oopn.getTests()) == 0

