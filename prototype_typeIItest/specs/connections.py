wire = {
    "type":"Wire",
    "start":"PresentPowerOutputs",
    "typeStart":"Switch",
    "end":"PresentPowerInputs",
    "typeEnd":"Light",
    "Healths":{
        "1":{
            "modality":"Health",
            "property":"health",
            "propertyvalues":["ok","broken"],
            "priorprobability":[0.99,0.01]
        }
    },
    "Behavior":{
        "normal": {
            'PresentPowerInputs' :   ["yes", "no",     "no", "yes"],
            'PresentPowerOutputs':   ["yes", "yes",    "no", "no"],
            'health'             :   ["ok",  "broken", "ok", "broken"]
        }
    }
}

wire2 = {
    "type":"Wire2",
    "start":"PresentLightOutputs",
    "typeStart":"Light",
    "end":"PresentPowerInputs",
    "typeEnd":"Switch",
    "Healths":{
        "1":{
            "modality":"Health",
            "property":"health",
            "propertyvalues":["ok","broken"],
            "priorprobability":[0.9,0.1]
        }
    },
    "Behavior":{
        "normal": {
            'PresentPowerOutputs':   ["yes"],
            'PresentPowerInputs' :   ["yes"],
            'health'             :   ["ok"]
        }
    }
}