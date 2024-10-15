Feature: Step arguments

    Scenario: Start diagnosis
        Given Repair specialist needs help diagnosing
        When System is started  
        Then CL1 should be in list of components 
        And No component is replaced
        And Test DT1 is present in list of available tests

    Scenario: Generate advice after component is in exception
        Given Repair specialist needs help diagnosing
        And Component CL1 is in exception state off
        When Evidence is presented and advice requested
        Then Advice on test DT1 is yes
        And Advice on test DT2 is no            

    Scenario: Test done and result presented
        Given Repair specialist needs help diagnosing
        And Component CL1 is in exception state off
        And Test DT1 is done, result RT1 is broken
        When Evidence is presented and advice requested
        Then Advice on test DT1 is yes
        And Advice on test DT2 is yes

    Scenario: Another Test done and result presented
        Given Repair specialist needs help diagnosing
        And Component CL1 is in exception state off
        And Test DT1 is done, result RT1 is broken
        And Test DT2 is done, result RT2 is broken
        When Evidence is presented and advice requested
        Then Advice on test DT1 is yes
        And Advice on test DT2 is yes                                 
        And Advice on replacement of CL1 via DRL1 is replace                 


#    Scenario: Component replaced, problem lies elsewhere
#        Given Repair specialist needs help diagnosing
#        And Component "CL1" has been replaced                    # L1H is OK
#        And Component "CL1" is in state "OFF"
#        When Evidence is presented and advice requested
#        Then Advice is to set component "S1" to state "On"

#    Scenario: Problem is solved, stop diagnosis
#        Given Repair specialist cleared the problem
#        When Signal "we're done" is received
#        Then All info is reset
#        And system returns to initial state

# additional features
# sorting of tests and suspected components in advice to test or replace
