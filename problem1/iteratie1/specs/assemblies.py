# small structure
structure1 = {
    "name":"structure1",
    "components": {
        "1":{
            "name":"Light",
            "type":"Light"
        },
        "2":{
            "name":"Switch",
            "type":"Switch"           
        }
    },
    "connections":{
        "1":{
            "name":"Wire",
            "type":"Wire",
            "startComponent":"Switch",
            "endComponent":"Light"
        }
    }
}

# bigger structure with more components and connections
structure3 = {
    "name":"structure3",
    "components": {
        "1":{
            "name":"Light",
            "type":"Light"
        },
        "2":{
            "name":"Switch",
            "type":"Switch"           
        },
        "3":{
            "name":"Light1",
            "type":"Light"
        },
        "4":{
            "name":"Switch1",
            "type":"Switch"           
        },
        "5":{
            "name":"Light2",
            "type":"Light"
        },
        "6":{
            "name":"Switch2",
            "type":"Switch"           
        },
    },
    "connections":{
        "1":{
            "name":"Wire",
            "type":"Wire",
            "startComponent":"Switch",
            "endComponent":"Light"
        },
        "2":{
            "name":"Wire2",
            "type":"Wire2",
            "startComponent":"Light",
            "endComponent":"Switch1"
        },
        "3":{
            "name":"Wire3",
            "type":"Wire",
            "startComponent":"Switch1",
            "endComponent":"Light1"
        },
        "4":{
            "name":"Wire4",
            "type":"Wire2",
            "startComponent":"Light1",
            "endComponent":"Switch2"
        },
        "5":{
            "name":"Wire5",
            "type":"Wire",
            "startComponent":"Switch2",
            "endComponent":"Light2"
        }

    }
}