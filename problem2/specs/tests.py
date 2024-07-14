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


