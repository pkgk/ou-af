import pytest
import pyAgrum
from problem2.src.oopn import Component, Connection, Assembly, ObserveTest
from problem2.specs.components import light, switch


### 
def test_CreateComponent():
        component = Component("switch", switch)
        assert component.getName() == "switch"
        assert component.getComponentNodeNames() == ['PresentPowerOutputsswitch', 'PresentPowerInputsswitch', 'EnabledStateInputsswitch', 'healthswitch']
        assert type(component.getVariables()[0]) == pyAgrum.LabelizedVariable
        assert type(component.getInternalConnections()[0]) == tuple
#        assert getCptOutput()
        assert component.getHealthVarName() == "healthswitch"
        assert component.getHealthPrior() == [0.99,0.01]
        assert component.getOutputsVarName() == "PresentPowerOutputsswitch"
        assert component.getInputsVarNames() == ['PresentPowerInputsswitch', 'EnabledStateInputsswitch']
        assert component.getInputPrior('PresentPowerInputsswitch') == [0.99,0.01]
