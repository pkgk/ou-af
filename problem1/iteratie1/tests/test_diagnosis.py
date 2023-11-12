""" test steps for diagnosis feature scenario's"""

from pytest_bdd import scenarios, given, when, then, parsers 
from extrataak.src.diagnosecontroller import DiagnosisController



# file to load containing influence diagram
lights_id_file = "res/lightv4.xml"  


# specify features file to get scenario's fromm
scenarios("diagnosis.feature")

# Scenario Start diagnosis
@given(parsers.parse("Repair specialist needs help diagnosing"), target_fixture="diagnosis_controller")
def init_diagnosis():
    """create instance of controller class as target_fixture"""
    return DiagnosisController()


@when(parsers.parse("System is started"))
def start_system(diagnosis_controller):
    """load influence diagram file to + get state of diagnosis
  
    assert initial state matched expected state
    """

    diagnosis_controller.load_influencediagram(lights_id_file)
    diagstate = diagnosis_controller.get_diagnosis_state()
    assert(diagstate ==   
           {'variables': {'HL1': {'labels': ['ok', 'broken']}, 'RT2': {'labels': ['not done', 'ok', 'broken']}, 'CL1': {'labels': ['on', 'off']}, 'RT1': {'labels': ['not done', 'ok', 'broken']}}, 
            'decisions': {'DT2': {'labels': ['yes', 'no']}, 'DRL1': {'labels': ['replace', 'keep']}, 'DT1': {'labels': ['yes', 'no']}}, 
            'utilities': {'URL1': {}, 'UT1': {}, 'UT2': {}}}
               )



@then(parsers.parse("{component} should be in list of components"))
def check_components(diagnosis_controller, component):
    """assert component is present in state"""
    diagnosis_state = diagnosis_controller.get_diagnosis_state()
    assert component in diagnosis_state["variables"]


@then(parsers.parse("No component is replaced"))
def check_replace_none(diagnosis_controller):
    """assert key "replaced is not present in state"""
    diagnosis_state = diagnosis_controller.get_diagnosis_state()
    for k in diagnosis_state["variables"]:
        assert "replaced"not in k


@then(parsers.parse("Test {expected_test} is present in list of available tests"))
def check_list_of_tests(diagnosis_controller, expected_test):
    """expected test is present in decisions"""
    diagnosis_state = diagnosis_controller.get_diagnosis_state()
    assert expected_test in diagnosis_state["decisions"]

def update_evidence(diagnosis_controller, component, state):
    """ set evidence for a component (chance variable or decision)"""
    # get state
    diagnosis_state = diagnosis_controller.get_diagnosis_state()
    # set evidence
    if component in diagnosis_state["variables"]:
        diagnosis_state["variables"][component]['evs'] = state
    elif component in diagnosis_state["variables"]:
        diagnosis_state["decisions"][component]['evs'] = state
    # set state
    diagnosis_controller.set_diagnosis_state(diagnosis_state)



# Scenario: Generate advice after component is in exception
@given(parsers.parse('Component {component} is in exception state {state}'))
def signal_component_exception(diagnosis_controller, component, state):
    """repair specialist has set evidence """
    diagnosis_controller.load_influencediagram(lights_id_file)
    update_evidence(diagnosis_controller, component, state)


@when(parsers.parse("Evidence is presented and advice requested"))
def process_evidence(diagnosis_controller):
    """evidence should be present in state, do inference,  
     process all decisions and put result in state"""
    diagnosis_controller.perform_inference()
    diagnosis_controller.process_decisions()


def get_decisions_from_state(diagnosis_controller):
    """ helper method to get state of all decisions in dict and return it"""
    output = {}
    state = diagnosis_controller.get_diagnosis_state()['decisions']
    for k in state:
        labelindex = state[k]['Advice'][0]
        label = state[k]['labels'][labelindex]
        output[k] = label
    return output

@then(parsers.parse("Advice on test {todotest} is {advice}"))
def advice_do_test(diagnosis_controller, todotest, advice):
    """"check if state after inference has advice on specified test"""
    assert get_decisions_from_state(diagnosis_controller)[todotest]
    assert advice  == get_decisions_from_state(diagnosis_controller)[todotest]


@then(parsers.parse("Advice on replacement of {component} via {decision} is {advice}"))
def advice_replace_component(diagnosis_controller, component, decision, advice):
    """"check if state after inference has advice on replacing a part"""
    assert get_decisions_from_state(diagnosis_controller)[decision]
    assert advice ==  get_decisions_from_state(diagnosis_controller)[decision]



#    Scenario: Test done and result presented
@given(parsers.parse("Test {test} is done, result {result} is {state}"))
def given_test_done(diagnosis_controller, test, result, state):
    """"set result of test as evidence """
    isdone = "yes"
    update_evidence(diagnosis_controller, test, isdone)
    update_evidence(diagnosis_controller, result, state)

