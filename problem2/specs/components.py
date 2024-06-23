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
    # normal behavior definition, example: all inputs:"yes" + output: "yes" + health:"ok" is a normal state (specified in "columns" below)
    "Behavior":{
        "normal": {
            'PresentPowerInputs':  ["yes", "yes","no" , "no", "yes",    "no",     "yes",    "no"], 
            'EnabledStateInputs':  ["yes", "no" ,"yes", "no", "yes",    "yes",    "no",     "no"],
            'PresentPowerOutputs': ["yes", "no" ,"no" , "no", "no",     "no",     "no",     "no"],
            'health':              ["ok",  "ok" , "ok", "ok", "broken", "broken", "broken", "broken"]
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
            "priorprobability":[0.99,0.01]
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
            "priorprobability":[0.8,0.01]
        }
    },
    "Behavior":{
        "normal": {
            'PresentPowerInputs':  ["yes", "no", "yes",    "no"], 
            'PresentLightOutputs': ["yes", "no", "no",    "no"],
            'health':              ["ok",  "ok", "broken", "broken"]
        }
    }
}


