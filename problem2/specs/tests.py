observeorreplacetest = {
        "name":"ObserveOrReplaceTest",
        "typeUndertest":"Light",
        "Testdecision":{
            "values":["yes", "no"]
        },
        "TestUtility":{
            "testcosts": -1,
        },
        "TestOutcome":{
            "testoutcomevalues":["ok","broken", "notdone"],
            "testoutcomeToReplaceDecision": False,
            "testoutcomecpt":{
                'health':                              ["ok"       , "ok"      , "broken"  , "broken"],
                'DecisionObserveOrReplaceTest':        ["no"       , "yes"     , "no"      , "yes"],
                "TestOutcomeObserveOrReplaceTest":     ["notdone"  , "ok"      , "notdone" , "broken"]
                },
        },
        "Replacedecision":{
                "name":"Replace",
                "values":["yes", "no"],
                "replacementcosts": -2,
                "incorrectreplacementcosts": -3,
                "failuretorepaircosts": -4
        }
    }


changeinputtest = {
        "name":"ChangeInputTest",
        "typeUndertest":"Light",
        "componentChain":{
            "start":"PresentPowerInputsSwitch",
            "end":"PresentLightOutputsLight"
        },
        "Testdecision":{
            "values":["yes", "no"]
        },
        "TestUtility":{
            "testcosts": -1,
        }
    }



testmapping1 = {
    "1":{
        "test":"ObserveOrReplaceTest",
        "target":"Light"
    }
}

testmapping11 = {
    "1":{
        "test":"ChangeInputTest",
        "target":"Light2"
    }
}


testmapping2 = {
    "1":{
        "test":"ObserveOrReplaceTest",
        "target":"Light"
    },
    "2":{
        "test":"ObserveOrReplaceTest",
        "target":"Switch"
    },
    "3":{
        "test":"ObserveOrReplaceTest",
        "target":"Wire"
    }

}



testmapping3 = {
    "1":{
        "test":"ObserveOrReplaceTest",
        "target":"Light"
    },
    "2":{
        "test":"ObserveOrReplaceTest",
        "target":"Light1"
    },
    "3":{
        "test":"ObserveOrReplaceTest",
        "target":"Light2"
    }
}

testmapping4 = {

}

testmapping5 = {
    "1":{
        "test":"ChangeInputTest",
        "target":"Switch"

    }
}



testmappinglight = {
    "1":{
        "test":"ObserveOrReplaceTest",
        "target":"Light"
    }
}

testmappingswitch = {
    "1":{
        "test":"ObserveOrReplaceTest",
        "target":"Switch"
    }
}

