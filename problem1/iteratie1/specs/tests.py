testObserveHealth = {
        "name":"TestObserveHealth",
        "typeUndertest":"Light",
        "decisionvalues":["yes", "no"],
        "testoutcomevalues":["ok","broken", "notdone"],
        "testoutcomeToReplaceDecision": False,
        "testcosts": -1,
        "testoutcomecpt":{
            'health':                           ["ok"       , "ok"      , "broken" , "broken"],
            'DecisionTestObserveHealth':        ["no"      , "yes"      , "no"    , "yes"],
            "TestOutcomeTestObserveHealth":     ["notdone"  , "ok" , "notdone" , "broken"]
        }
    }

testmapping1 = {
    "1":{
        "test":"TestObserveHealth",
        "target":"Light"
    }
}


testmapping3 = {
    "1":{
        "test":"TestObserveHealth",
        "target":"Light"
    },
    "2":{
        "test":"TestObserveHealth",
        "target":"Light1"
    },
    "3":{
        "test":"TestObserveHealth",
        "target":"Light2"
    }
}