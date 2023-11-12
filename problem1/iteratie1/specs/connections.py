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
            "priorprobability":[0.9,0.1]
        }
    },
    "Behavior":{
        "normal": {
            'PresentPowerInputs' :   ["yes"],
            'PresentPowerOutputs':   ["yes"],
            'health'             :   ["ok"]
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