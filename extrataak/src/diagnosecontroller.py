"""module to help diagnosis with knowledge from influence diagram"""


# imports
import pyAgrum as gum


class DiagnosisController:

    """Controlleer class 
    - takes input from interaction with user via a datastructure
    - loads influence diagram, performs inference and provides results
    - provides advice on which test to carry out and what component to replace
    """

    def __init__(self):
        """init of class

        variables:
        diag -- influence diagram (default empty dict)
        diagnosis_state -- state of diagnosis, data structure supporting interaction (default empty dict)
        ie -- inference object (default None)
        """
        self.diag = gum.InfluenceDiagram()
        self.diagnosis_state = {}
        self.ie = None


    def load_influencediagram(self, idfile):
        """load influence diagram from given file
        
        arguments:
        idfile -- path to file containing influence diagram in BIFXML format

        returns: 
        nothing -- when no error
        filenotfound -- error from exception FileNotFoundError
        """
        try:
            self.diag.loadBIFXML(idfile)
            self.diagnosis_state = self.generate_diagnosis_state()
        except FileNotFoundError as filenotfound:
            return filenotfound

    def get_diagnosis_state(self):
        """return current state of diagnosis"""
        return self.diagnosis_state

    def set_diagnosis_state(self, state):
        """set current state of diagnosis"""
        self.diagnosis_state = state

    def generate_diagnosis_state(self):
        """generate initial state of diagnosis based on variables, decisions and utilities of influence diagram
        
        for chance variables and decisions: add labels
        return: dict with variables, decisions and utilities from influence diagram + labels 
        """
        cvdict = {}
        for cv in self.get_chance_variables():
            labellist = []
            for l in self.diag.variable(cv).labels():
                labellist.append(l)
            dl = {"labels":labellist}
            cvdict[cv] = dl
        dvdict = {}
        for dv in self.get_decision_variables():
            decisionlabellist = []
            for l in self.diag.variable(dv).labels():
                decisionlabellist.append(l)
            ddl = {"labels":decisionlabellist}
            dvdict[dv] = ddl
        uvdict = {}
        for uv in self.get_utility_variables():
            uvdict[uv] = {}
        print(self.get_chance_variables())
        return {"variables":cvdict,
                 "decisions":dvdict,
                  "utilities":uvdict}


    def print_cpt(self, chancevar):
        """ method to print probabilities of a chance variable
        
        arguments:
        chancevar -- variable for which probability table needs to be printed
        """
        print(self.diag.cpt(chancevar))


    def get_chance_variables(self):
        """ method to get all chance variables
        
        return:
        chance_variables -- list of all chance variables in influence diagram
        """
        chance_variables = []
        for i in self.diag.names():
            if self.diag.isChanceNode(i):
                chance_variables.append(i)
        return chance_variables

    def get_decision_variables(self):
        """ method to get all decisions
        
        return:
        decision_variables -- list of all decisions in influence diagram
        """        
        decision_variables = []
        for i in self.diag.names():
            if self.diag.isDecisionNode(i):
                decision_variables.append(i)
        return decision_variables

    def get_utility_variables(self):
        """ method to get all utilities
        
        return:
        utility_variables -- list of all utilities in influence diagram
        """        
        utility_variables = []
        for i in self.diag.names():
            if self.diag.isUtilityNode(i):
                utility_variables.append(i)
        return utility_variables


    def perform_inference(self):
        """ method to make inference"""
        # initialize inference object 
        self.ie = gum.ShaferShenoyLIMIDInference(self.diag)
        # get evidence from state structure and set to inference object
        self.ie.setEvidence(self.get_evidence_from_state())
        # do inference
        self.ie.makeInference()


    def process_decisions(self):
        """ return decisions from posterior probabilities
        
        - places a tuple in the datastructure at a decision variable
        - tuple is filled with maximum probability from argmax function on 
        potential object that represents the posterior probability of a decision
        """
        for decision in self.diagnosis_state["decisions"]:
            # derive and set "advice" key per decision
            self.diagnosis_state["decisions"][decision]['Advice'] = (                     
                        # create tuple
                        (                                                                 
                        # get state with highest probability via argmax
                        self.ie.posterior(decision).argmax()[0][0][decision],             
                        # include posterior probability
                        self.ie.posterior(decision).argmax()[1]                           
                        )
            )

    def set_evidence(self, group, key, state):
        """ set evidence (state) for group (variable/decisions), key (component) 
        
        arguments:
        group -- variables or decisions "group" in datastructure
        key -- key of variable or decision in datastructure
        state -- label representing state of variable/decision        
        """
        self.diagnosis_state[group][key]['evs'] = state


    def get_evidence_from_state(self):
        """ return evidence from the diagnosis_state (variables or decisions) 
        used to set evidence before inference        
        """
        result = {}
        # loop variables
        state = self.diagnosis_state['variables']
        for e in state:
            if state[e].get("evs") != None:
                result[e] = state[e]['evs']
        state = self.diagnosis_state['decisions']
        for e in state:
            if state[e].get("evs") != None:
                result[e] = state[e]['evs']
        return result
        


    