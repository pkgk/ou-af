components = {
    "wiper" : {
        "type":"wiper",
        "Inputs": {
            "1" : {
                "modality":"Power",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "2" : {
                "modality":"Control_signal",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"Movement",
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
        "Behavior":{
            "normal": {
                'PresentPowerInputs':           ["yes"], 
                'PresentControl_signalInputs':  ["yes"],
                'health':                       ["ok"],
                'PresentMovementOutputs':       ["yes"]
            }
        } 
    },
    "lens" : {
        "type":"lens",
        "Inputs": {
            "1" : {
                "modality":"Laserbeam",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"FocussedLaserbeam",
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
        "Behavior":{
            "normal": {
                'PresentLaserbeamInputs':                   ["yes"],
                'health':                                   ["ok"],
                'PresentFocussedLaserbeamOutputs':          ["yes"]
            }
        } 
    },
    "tilted_mirror" : {
        "type":"tilted_mirror",
        "Inputs": {
            "1" : {
                "modality":"FocussedLaserbeam",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "2" : {
                "modality":"Power",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "3" : {
                "modality":"ControlSignal",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"MovingBeam",
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
        "Behavior":{
            "normal": {
                'PresentFocussedLaserbeamInputs':       ["yes"],
                'PresentPowerInputs':                   ["yes"],
                'PresentControlSignalInputs':           ["yes"],
                'health':                               ["ok"],
                'PresentMovingBeamOutputs':             ["yes"]
            }
        } 
    },
    "developer_roll" : {
        "type":"developer_roll",
        "Inputs": {
            "1" : {
                "modality":"Power",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "2" : {
                "modality":"TonerParticles",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"MovingTonerParticles",
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
        "Behavior":{
            "normal": {
                'PresentPowerInputs':                   ["yes"], 
                'PresentTonerParticlesInputs':          ["yes"],
                'health':                               ["ok"],
                'PresentMovingTonerParticlesOutputs':   ["yes"]
            }
        } 
    },
    "charge_roll" : {
        "type":"charge_roll",
        "Inputs": {
            "1" : {
                "modality":"Power",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"ElectricalCharge",
                "property":"Present",
                "propertyvalues":["yes", "no"]
                }
            },
        "Healths":{
            "1":{
                "modality":"Health",
                "property":"health",
                "propertyvalues":["ok","broken"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Behavior":{
            "normal": {
                'PresentPowerInputs':                   ["yes"],
                'health':                               ["ok"],
                'PresentElectricalChargeOutputs':       ["yes"]
            }
        } 
    },
    "drum" : {
        "type":"drum",
        "Inputs": {
            "1" : {
                "modality":"Movement",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "2" : {
                "modality":"MovingBeam",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "3" : {
                "modality":"MovingTonerParticles",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                },
            "4" : {
                "modality":"ElectricalCharge",
                "property":"Present",
                "propertyvalues":["yes", "no"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Outputs":{
            "1":{
                "modality":"ImageInToner",
                "property":"Present",
                "propertyvalues":["yes", "no"]
                }
            },
        "Healths":{
            "1":{
                "modality":"Health",
                "property":"health",
                "propertyvalues":["ok","broken"],
                "priorprobability":[0.98,0.02]
                }
            },
        "Behavior":{
            "normal": {
                'PresentMovementInputs':                ["yes"],
                'PresentMovingBeamInputs':              ["yes"],
                'PresentMovingTonerParticlesInputs':    ["yes"],
                'PresentElectricalChargeInputs':        ["yes"],
                'health':                               ["ok"],
                'PresentImageInTonerOutputs':           ["yes"]
                }
            } 
    }
}