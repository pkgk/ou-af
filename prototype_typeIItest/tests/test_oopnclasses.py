import pytest
import pyAgrum
from problem2.src.oopnclasses import Component, Connection, Oopn, ObserveOrReplaceTest, Node
from problem2.specs.components import light, switch
from problem2.specs.connections import wire
from problem2.specs.tests import observeorreplacetest, testmappingswitch


### 
def test_CreateComponent():

     cpttable = {    'PresentPowerInputsswitch': 'yes',
                        'EnabledStateInputsswitch': 'yes',
                        'PresentPowerOutputsswitch': 'yes',
                        'healthswitch': 'ok'}
        
     component = Component("switch", switch)
     assert component.getName() == "switch"

     assert component.getComponentNodeNames() == ['PresentPowerOutputsswitch', 'PresentPowerInputsswitch', 'EnabledStateInputsswitch', 'healthswitch']
     assert len(component.getNodes()) == 4
     assert type(component.getNodes()[0]) == Node
     assert type(component.getNodes()[0].getVariable()) == pyAgrum.LabelizedVariable
     assert type(component.getNodeVariables()[0]) == pyAgrum.LabelizedVariable
     assert type(component.getInternalConnections()[0]) == tuple

     assert component.getHealthVarName() == "healthswitch"
     assert component.getOutputsVarName() == "PresentPowerOutputsswitch"
     assert component.getInputsVarNames() == ['PresentPowerInputsswitch', 'EnabledStateInputsswitch']

     for c in component.getNodes():
          if (c.getType() == "Output"):
               assert type(c.getPrior() == pyAgrum.Potential)
               for p in c.getPrior().loopIn():
                    assert type(p) == pyAgrum.Instantiation
     assert type(component.getHealthNode().getVariable() == pyAgrum.LabelizedVariable)
     assert type(component.getHealthPrior() == pyAgrum.Potential) 
     for node in component.getInputNodes():
          assert type(node.getPrior()) == pyAgrum.Potential   


def test_createConnection():  

     component1 = Component("switch", switch)
     component2 = Component("light", light)
     connection = Connection("wire", wire, component1, component2)
     assert type(connection.getEndNode()) == Node
     assert type(connection.getStartNode()) == Node
     assert connection.getStartNode().getName() == "PresentPowerOutputsswitch"
#     assert connection.setCptEndNode() == 2


def test_ObserveOrReplaceTest():
     component = Component("Switch", switch)
     for key, test in testmappingswitch.items():
          testname = test["test"]
          testtarget = test["target"]
          break
     assert testname == "ObserveOrReplaceTest"
     assert testtarget == "Switch"
     ortest = ObserveOrReplaceTest(testname, component, observeorreplacetest)
     assert type(ortest) == ObserveOrReplaceTest
     assert ortest.getName() == "ObserveOrReplaceTest"
     assert ortest.getTarget().getName() == "Switch"
     assert ortest.getTestDecision().getName() == "DecisionObserveOrReplaceTestSwitch"
     assert ortest.getTestUtility().getName() == "UtilityObserveOrReplaceTestSwitch"
     assert ortest.getTestOutcome().getVariable().labels() == ("ok", "broken", "notdone")
     assert ortest.getReplaceDecision().getName() == "DecisionReplaceSwitch"
     assert ortest.getReplaceUtility().getVariable().labels() == ("0",)
     assert type(ortest.getNodes()) == list
     assert ortest.getInternalConnections()[0] == ("DecisionObserveOrReplaceTestSwitch", "UtilityObserveOrReplaceTestSwitch")
     assert type(ortest.getTestOutcome().getPrior()) == pyAgrum.Potential
     assert type(ortest.getTestUtility().getPrior()) == pyAgrum.Potential


     