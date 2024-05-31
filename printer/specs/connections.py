laserbeam = {
    "type":"laserbeam",
    "start":"PresentFocussedLaserbeamOutputs",
    "typeStart":"lens",
    "end":"PresentFocussedLaserbeamInputs",
    "typeEnd":"tilted_mirror",
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
            'PresentFocussedLaserbeamInputs' :   ["yes", "no",     "no", "yes"],
            'PresentFocussedLaserbeamOutputs':   ["yes", "yes",    "no", "no"],
            'health'                         :   ["ok",  "broken", "ok", "broken"]
        }
    }
}

wipercontact = {
    "type":"wipercontact",
    "start":"PresentMovementOutputs",
    "typeStart":"wiperblade",
    "end":"PresentMovementInputs",
    "typeEnd":"drum",
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

rollcontact = {
    "type":"rollcontact",
    "start":"PresentMovingTonerParticlesOutputs",
    "typeStart":"developer_roll",
    "end":"PresentMovingTonerParticlesInputs",
    "typeEnd":"drum",
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

charge = {
    "type":"charge",
    "start":"PresentElectricalChargeOutputs",
    "typeStart":"charge_roll",
    "end":"PresentElectricalChargeInputs",
    "typeEnd":"drum",
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

movingbeam = {
    "type":"movingbeam",
    "start":"PresentMovingBeamOutputs",
    "typeStart":"tilted_mirror",
    "end":"PresentMovingBeamInputs",
    "typeEnd":"drum",
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
            'PresentFocussedLaserbeamInputs' :   ["yes", "no",     "no", "yes"],
            'PresentFocussedLaserbeamOutputs':   ["yes", "yes",    "no", "no"],
            'health'                         :   ["ok",  "broken", "ok", "broken"]
        }
    }
}