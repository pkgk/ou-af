testObserveHealth = {
        "name":"TestObserveHealth",
        "typeUndertest":"Light",
        "decisionvalues":["yes", "no"],
        "testoutcomevalues":["ok","broken", "notdone"],
        "testoutcomeToReplaceDecision": True,
        "testcosts": -2,
        "testoutcomecpt":{
            'health':                           ["ok"       , "ok"      , "broken" , "broken"],
            'DecisionTestObserveHealth':        ["yes"      , "no"      , "yes"    , "no"],
            "TestOutcomeTestObserveHealth":     ["ok"       , "notdone" , "broken" , "notdone"]
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