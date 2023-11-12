# component Switch > Python datastructure dictionary

switch = {
    "type":"Switch",
    "Inputs":{
        "1":{
            "modality":"Power",
            "property":"Present",
            "propertyvalues":["yes", "no"],
            "priorprobability":[0.99,0.01]        },
        "2":
        {
            "modality":"State",
            "property":"Enabled",
            "propertyvalues":["yes", "no"],
            "priorprobability":[0.99,0.01]        }
    },
    "Outputs":{
        "1":{
            "modality":"Power",
            "property":"Present",
            "propertyvalues":["yes", "no"]
        }
    },
    "Healths":{
        "1":{
            "modality":"Health",
            "property":"health",
            "propertyvalues":["ok","broken"],
            "priorprobability":[0.99,0.01]
        }
    },
    "Decisions":{
        "1":{
            "name":"Replace",
            "values":["yes", "no"],
            "replacementcosts": -2,
            "incorrectreplacementcosts": -3,
            "failuretorepaircosts": -4
            }
    },
    # normal behavior definition, example: all inputs:"yes" + output: "yes" + health:"ok" is a normal state (specified in "columns" below)
    "Behavior":{
        "normal": {
            'PresentPowerInputs':  ["yes", "yes","no" , "no"], 
            'EnabledStateInputs':  ["yes", "no" ,"yes", "no"],
            'PresentPowerOutputs': ["yes", "no" ,"no" , "no"],
            'health':              ["ok",  "ok" , "ok", "ok"]
        }
    }
}


# component Light > Python datastructure dictionary

light = {
    "type":"Light",
    "Inputs":{
        "1":{
            "modality":"Power",
            "property":"Present",
            "propertyvalues":["yes", "no"],
            "priorprobability":[0.9,0.1]
        }
    },
    "Outputs":{
        "1":{
            "modality":"Light",
            "property":"Present",
            "propertyvalues":["yes", "no"]
        }
    },
    "Healths":{
        "1":{
            "modality":"Health",
            "property":"health",
            "propertyvalues":["ok","broken"],
            "priorprobability":[0.9,0.1]
        }
    },
    "Decisions":{
        "1":{
            "name":"Replace",
            "values":["yes", "no"],
            "replacementcosts": -2,
            "incorrectreplacementcosts": -3,
            "failuretorepaircosts": -4
        }
    },
    "Behavior":{
        "normal": {
            'PresentPowerInputs':  ["yes", "no"], 
            'PresentLightOutputs': ["yes", "no"],
            'health':              ["ok",  "ok"]
        }
    }

}


