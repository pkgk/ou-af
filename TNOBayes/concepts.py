
from typing import Any, Dict, Optional, Tuple, Iterator, Sequence, Union, Iterable, TypeVar, Set, List, Type, Generic
from collections import Counter
from inspect import getmembers, isclass
from itertools import chain
import abc
import inspect
from enum import Enum
from more_itertools import first_true


SPLITCHAR = "."  # separator between names in hierarchical structure

def abbreviated(name: str):
    """ Removes the first part of the name """
    elements = name.split(SPLITCHAR)
    return SPLITCHAR.join(elements[1:])

class Singleton():
    def __copy__(self):
        return self
    def __deepcopy__(self, _):
        return self


class Anything(Singleton): pass
ANY = Anything()

class SAME():
    def __init__(self, index:int):
        """ Indicates that the output is identical to the inputs specified by index.
        Index starts at 1.
        """
        self.index:int = index  

class SYSTEMType(Singleton): pass
SYSTEM = SYSTEMType()  # denotes top-level system (no parent)

class NamedObject():
    def __init__(self, parent:Union["NamedObject", SYSTEMType], name:str):
        self.parent = parent
        self.name:str = name if isinstance(parent, SYSTEMType) else parent.name + SPLITCHAR + name 

    def __str__(self):
        return self.name

    def extendName(self, postfix: str):
        return self.name + SPLITCHAR + postfix

    @property
    def shortName(self):
        """ Removes the first part of the name that is typically the system name"""
        short = self.name[self.name.rfind(SPLITCHAR)+1:]
        return short

# Modalities
Property = Enum
SingleItem = Union[Property,Anything]
Impossible = Tuple[SingleItem, ...]

class Modality():
    allImpossibles: Dict[Any,List[Impossible]] = {}

    @classmethod 
    def _checkImpossibles(cls, impossibles:List[Impossible]):
        typelist = [t for t in vars(cls).values() if isclass(t) and issubclass(t, Property)]
        for impossible in impossibles:
            assert len(impossible) == len(typelist), \
                f"Impossible definition for {cls} has {len(impossible)} elements but expected {len(typelist)}"
            for element, expectedType in zip(impossible, typelist):
                assert element is ANY or type(element) == expectedType, \
                    f"Impossible definition for {cls} has element {element} of type {type(element)} but expected {expectedType}"

    @classmethod
    def addImpossible(cls, *impossibles:Impossible):
        listOfImpossibles = list(impossibles)
        cls._checkImpossibles(listOfImpossibles)
        try:
            cls.allImpossibles[cls].extend(impossibles)
        except KeyError:
            cls.allImpossibles[cls] = listOfImpossibles

    @classmethod
    def getImpossibles(cls) -> List[Impossible]:
        # find all impossibles by walking up the inheritance chain
        result: List[Impossible] = []
        for c in cls.mro():
            if issubclass(c, Modality): 
                result.extend(c.allImpossibles.get(c, []))
        return result

# Connectors

class Connector(NamedObject): 
    def __init__(self, parent:Union["Component","State"], name:str):
        super().__init__(parent, name)

    def getProperties(self) -> Sequence[Tuple[str,Property]]:
        """ Return all properties in declared order"""
        # getmembers returns members in alphabetical order!
        return getmembers(self, lambda value:isclass(value) and issubclass(value,Property))

    def getModality(self) -> Type[Modality]:
        # TODO: maybe Generic type hinting can do better job
        for superclass in type(self).mro():
            if issubclass(superclass, Modality):
                return superclass 
        assert False, f"no modality for {self.name}"
    
    def alwaysVisible(self):
        return False

class Input(Connector): pass
class Output(Connector): pass

CanDo = Property('CanDo', 'CAN CANNOT')
class Able(Modality):
    able = CanDo
class CapabilityPort(Able): pass
class CapabilityInput(Input, CapabilityPort): pass
class CapabilityOutput(Output, CapabilityPort): pass

# Health
class Health(Modality):
    name:Optional[str] = None

Clause = Union[Anything, Input]
Consequence = Union[SAME, Output]
InputStates = Sequence[Clause]
OutputStates = Sequence[Consequence]
Prob = float
Rule = Union[Tuple[InputStates, OutputStates], Tuple[InputStates, OutputStates, Prob]]

Relation = Sequence[Rule]

ELSE:InputStates = []
ALWAYS:InputStates = []

class Normal(Health):
    def __init__(self, relation:Relation):
        self.relation = relation

class Failure(Health):
    def __init__(self, name:str, prior:Prob, relation:Relation):
        self.name:str = name
        self.relation:Relation = relation
        self.prior:Prob = prior

# Unreliable things can fail
class Unreliable():
    def __init__(self):
        self.normal: Optional[Normal] = None # By default, everything is normal
        self.failures: List[Failure] = []   # By default connections are assumed to be flawless
        self.name = "#Unknown"

    def _checkSpec(self, relationName:str, relation:Relation):
        # little hack for now
        if isinstance(self, Component):
            inputtypelist = [prop[1] for inp in self.getInputs() for prop in inp.getProperties()]
            outputtypelist = [prop[1] for outp in self.getOutputs() for prop in outp.getProperties()]
        elif isinstance(self, Connection):
            inputtypelist = [prop[1] for prop in self.input.getProperties()]
            outputtypelist = [prop[1] for prop in self.output.getProperties()]
        else:
            assert False, f"Cannot check specification for {self.name} of type {type(self)}: not yet implemented"

        for rule in relation:
            condition, result, *_ = rule
            if condition is not ELSE and condition is not ALWAYS:
                assert len(condition) == len(inputtypelist), \
                    f"Number of elements in condition for {relationName} of {type(self)} is {len(condition)} but expected {len(inputtypelist)}"
                for element, requiredType in zip(condition, inputtypelist):
                    if element is not ANY:
                        assert type(element) == requiredType, \
                            f"Type mismatch in condition {relationName} of {type(self)}: expected {requiredType} but got {type(element)}"

            for element, requiredType in zip(result, outputtypelist):
                    if isinstance(element, SAME):
                        assert 1 <= element.index <= len(inputtypelist), \
                            f"SAME({element.index}) refers to unknown input. Number must be in [1..{len(inputtypelist)}]"
                        assert inputtypelist[element.index-1] == requiredType, \
                            f"SAME({element.index}) in {relationName} of {type(self)} refers to type {inputtypelist[element.index-1]} but expected {requiredType}"
                    else:
                        assert type(element) == requiredType, \
                            f"Type mismatch in result {relationName} of {type(self)}: expected {requiredType} but got {type(element)}"


    def setNormal(self, relation: Relation) -> None:
        print(f"setting normal for {self.name}")
        assert self.normal is None, f"Multiple Normal definitions for component {self.name}"
        self._checkSpec("normal", relation)
        self.normal = Normal(relation)

    def addFailure(self, name:str, priorProb:Prob, relation:Relation) -> None:
        self._checkSpec(name, relation)
        self.failures.append(Failure(name, priorProb, relation))

    def getFailure(self, name:str) -> Failure:
        failure = first_true(self.failures, pred=lambda f: f.name == name, default=None)
        assert failure is not None, f"could not find failure {name} for {self.name}"
        #assert isinstance(failure, Failure), f"failure is not of type Failure but {type(failure)}"
        return failure


# Connections

Tin = TypeVar("Tin", bound=Input)
Tout = TypeVar("Tout", bound=Output)

class Connection(Unreliable, Generic[Tout,Tin]):
    __metaclass__ = abc.ABCMeta

    def __init__(self, input: Tout, output: Tin):
        super().__init__()
        assert isinstance(input, Output), f"Connection input is not an output connector"
        assert isinstance(output, Input), f"Connection output is not an input connector"
        self.input:Tout = input
        self.output:Tin = output
        self.name = f"{self.getDescriptor()} connecting {abbreviated(self.input.name)} ---> {abbreviated(self.output.name)}"
        self.parent = inspect.currentframe().f_back.f_back.f_locals['self']  # type:ignore Find calling object. 

    def __str__(self):
        return self.getName()
        
    def getConnectors(self) -> Iterator[Optional[Connector]]:
        yield self.input
        yield self.output

    @abc.abstractmethod
    def getDescriptor(self) -> str:
        raise NotImplementedError()

    def getName(self):        
        return self.name

# Module
def isIterable(attr: Any) -> bool:
    """ Checks if an attribute is iterable, with exception of strings """
    return isinstance(attr, Iterable) and not isinstance(attr, str)


class Module(NamedObject):
    def __init__(self, parent: Union["Module", SYSTEMType], name:str):
        super().__init__(parent, name)

    #TODO make generic functions
    def getModules(self, recursive:bool=False) -> Iterator['Module']:
        for attr in vars(self).values():
            if isinstance(attr, Module) and attr != self.parent:
                yield attr
                if recursive:
                    yield from attr.getModules(recursive)
            elif isIterable(attr):
                assert isinstance(attr, Iterable)
                for elt in attr:
                    if isinstance(elt, Module):
                        yield elt
                        if recursive:
                            yield from elt.getModules(recursive)

    def getAssemblies(self, recursive:bool=False) -> Iterator['Assembly']:
        for attr in vars(self).values():
            if isinstance(attr, Assembly) and attr != self.parent:
                yield attr
                if recursive:
                    yield from attr.getAssemblies(recursive)
            elif isIterable(attr):
                assert isinstance(attr, Iterable)
                for elt in attr:
                    if isinstance(elt, Assembly):
                        yield elt
                        if recursive:
                            yield from elt.getAssemblies(recursive)   

    def getComponents(self, recursive:bool=False) -> Iterator['Component']:
        for attr in vars(self).values():
            if isinstance(attr, Module) and attr != self.parent:
                if isinstance(attr, Component):
                    yield attr
                if recursive:
                    yield from attr.getComponents(recursive)
            elif isIterable(attr):
                assert isinstance(attr, Iterable)
                for elt in attr:
                    if isinstance(elt, Module) and attr != self.parent:
                        if isinstance(elt, Component):
                            yield elt
                        if recursive:
                            yield from elt.getComponents(recursive)

    def getCapabilities(self, recursive:bool=False) -> Iterator['Capability']:
        for attr in vars(self).values():
            if isinstance(attr, Module) and attr != self.parent:
                if isinstance(attr, Capability):
                    yield attr
                if recursive:
                    yield from attr.getCapabilities(recursive)
            elif isIterable(attr):
                assert isinstance(attr, Iterable)
                for elt in attr:
                    if isinstance(elt, Module) and attr != self.parent:
                        if isinstance(elt, Capability):
                            yield elt
                        if recursive:
                            yield from elt.getCapabilities(recursive)


    def getConnectors(self, recursive:bool=False) -> Iterator[Connector]:
        for name, attr in vars(self).items():
            if name in ["parent", "name", "elements"]:  # TODO: improve this hack
                continue
            try:
                if attr in self.elements: #type: ignore : protected by try-except
                    continue
            except AttributeError:
                pass
            if isinstance(attr, Connector):
                yield attr
            elif isIterable(attr):
                yield from (elt for elt in attr if isinstance(elt, Connector))
                if recursive:
                    for elt in attr:
                        if isinstance(elt, Module):
                            yield from elt.getConnectors(recursive)
            elif recursive and isinstance(attr, Module) and attr != self.parent:
                yield from attr.getConnectors(recursive)

    def getOutputs(self, recursive:bool=False) -> Iterator[Output]:
        for name, attr in vars(self).items():
            if name in ["parent", "name", "elements"]:  # TODO: improve this hack that is needed for SuperCmponents
                continue
            try:
                if attr in self.elements: #type: ignore : protected by try-except
                    continue
            except AttributeError:
                pass
            if isinstance(attr, Output):
                yield attr
            elif isIterable(attr):
                yield from (elt for elt in attr if isinstance(elt, Output))
                if recursive:
                    for elt in attr:
                        if isinstance(elt, Module):
                            yield from elt.getOutputs(recursive)
            elif recursive and isinstance(attr, Module) and attr != self.parent:
                yield from attr.getOutputs(recursive)

    def getInputs(self, recursive:bool=False) -> Iterator[Input]:
        for name, attr in vars(self).items():
            if name in ["parent", "name", "elements"]:  # TODO: improve this hack that is needed for SuperCmponents
                continue
            try:
                if attr in self.elements: #type: ignore : protected by try-except
                    continue
            except AttributeError:
                pass
            if isinstance(attr, Input):
                yield attr
            elif isIterable(attr):
                yield from (elt for elt in attr if isinstance(elt, Input))
                if recursive:
                    for elt in attr:
                        if isinstance(elt, Module):
                            yield from elt.getInputs(recursive)
            elif recursive and isinstance(attr, Module) and attr != self.parent:
                yield from attr.getInputs(recursive)

    def getConnections(self, recursive:bool=False) -> Iterator[Connection]:
        if isinstance(self, Assembly):
            yield from self.connections
            if recursive:
                for attr in vars(self).values():
                    if isIterable(attr):
                        for elt in attr:
                            if isinstance(elt, Assembly):
                                yield from elt.getConnections(recursive)
                    if isinstance(attr, Module) and attr != self.parent:
                        yield from attr.getConnections(recursive)

    def getDummyConnections(self, recursive:bool=False) -> Iterator[Connection]:
        if isinstance(self, Assembly):
            yield from self.dummyConnections
            if recursive:
                for attr in vars(self).values():
                    if isIterable(attr):
                        for elt in attr:
                            if isinstance(elt, Assembly):
                                yield from elt.getDummyConnections(recursive)
                    if isinstance(attr, Module) and attr != self.parent:
                        yield from attr.getDummyConnections(recursive)

    def getUnusedConnections(self, recursive:bool=False) -> Iterator[Connection]:
        if isinstance(self, Assembly):
            yield from self.unusedConnections
            if recursive:
                for attr in vars(self).values():
                    if isIterable(attr):
                        for elt in attr:
                            if isinstance(elt, Assembly):
                                yield from elt.getUnusedConnections(recursive)
                    if isinstance(attr, Module) and attr != self.parent:
                        yield from attr.getUnusedConnections(recursive)

    def openInputs(self) -> Set[Input]:
        connections = self.getConnections(recursive=True)
        inputsUsed = set(connection.output for connection in connections)
        allInputs = set(self.getInputs(recursive=True))
        inputsNotUsed = allInputs - inputsUsed

        return inputsNotUsed

# Capabilities

HealthStates = Union[Unreliable,Tuple[Unreliable, Sequence[str]]]

class Capability(Module, CapabilityOutput, Unreliable): #TODO: distinguish between Capability and other unreliable things? Maybe not...
    """ Capability that can take any series components as well as other capabilities
    """
    #TODO: support capabilities with multiple states
    def __init__(self, parent: "Assembly", name:str, *inputs:HealthStates):
        """ Defines a capability

        name: full name of the capability
        inputs: a sequence of either 
                    - Unreliable (component or other capability). This assumes that the first state is the only state
                      that is OK.
                or 
                    - a tuple (Unreliable, sequence of statenames) where the statenames indicate which states are considered
                      to be OK for this capability.
        Note that currently only "AND" logic is supported for capabilities and that capabilities have the states CAN and CANNOT
        """
        super().__init__(parent, name)
        #super(CapabilityOutput).__init__(self, "output")
        super(Unreliable).__init__()
        # Check parameters to fail fast
        self.inputs: List[HealthStates] = []
        self.addInputs(*inputs)
    
    #self.output = CapabilityOutput(self, "cando")


    def addInputs(self, *inputs: HealthStates) -> None:
        """ Add inputs for this capability """
        for input in inputs:
            if isinstance(input, tuple):
                assert len(input) == 2, f"Component health state must have 2 components but has {len(input)}"
                unreliable = input[0]
                assert not isinstance(unreliable, Capability), "Capabilities cannot have good state definition"
                #TODO: support capabilities with multiple states
                goodstatenames = input[1]
            else:
                unreliable = input
                goodstatenames = ["OK"]
            for goodstatename in goodstatenames:
                assert goodstatename == "OK" or goodstatename in [failure.name for failure in unreliable.failures], \
                    f"State {goodstatename} is not defined for component {unreliable.name}"
            
            self.inputs.append((unreliable, goodstatenames))  



# Components

Composite = Union[SYSTEMType, "Assembly", "SuperComponent"]

class Component(Module, Unreliable):
    """ Base class for components

    Components define relations between inputs and outputs for normal and failure mode behaviors.
    """
    def __init__(self, parent: Composite, name:str):
        super().__init__(parent, name)
        super(Unreliable).__init__()
        self.normal: Optional[Normal] = None  # indicates not specified, so everything is considered normal: this component cannot fail
        self.failures: List[Failure] = []


class SuperComponent(Component):
    def __init__(self, parent:Composite, name:str):
        super().__init__(parent, name)
        self.elements: List[Unreliable] = []
        self.primitiveFailures: List[Failure] = []

    def addFailure(self, name:str, priorProb:Prob, relation:Relation) -> None:
        assert False, f"Method 'addFailure' should not be used for SuperComponent {self.name}. Use 'addFailures' instead."

    def addFailures(self, name: str, relation: Relation, *failurespecs: Tuple[Unreliable, Iterable[str]]) -> None:
        """ add failures that lead to the same effect """
        productProb = 1.0
        for element, failurenames in failurespecs:
            totalProb = 0.0
            for failurename in failurenames:
                failure = element.getFailure(failurename)
                assert failure not in self.primitiveFailures, f"Failure {failure.name} for {element.name} already incorporated"
                totalProb += failure.prior
                self.primitiveFailures.append(failure)

            productProb *= (1.0 - totalProb)
        
        super().addFailure(name, 1.0-productProb, relation)    

    def addDefaultFailure(self, name:str, relation:Relation):
        """ all other failures lead to this behavior """
        productProb = 1.0
        for element in self.elements: 
            totalProb = 0.0
            for failure in element.failures:
                if failure not in self.primitiveFailures:
                    totalProb += failure.prior
                    self.primitiveFailures.append(failure)  
            productProb *= (1.0 - totalProb)
        super().addFailure(name, 1.0-productProb, relation)

    def checkFailuresComplete(self) -> None: 
        """ checks if all failures of all elements are covered exactly once """
        allFailures = (failure for element in self.elements for failure in element.failures)
        counterAllFailures = Counter(allFailures)
        counterKnownFailures = Counter(self.primitiveFailures)
        if counterAllFailures != counterKnownFailures:
            counterAllFailures.subtract(counterKnownFailures)
            for failure in counterAllFailures.elements():
                print(f"DIFFERENCE FOR: {failure.name}")        
            assert False, f"Not all failures covered in {self.name}"

    TU = TypeVar("TU", bound=Unreliable) 
    def addElement(self, element: TU) -> TU:
        self.elements.append(element)
        return element

# Assemblies

class Assembly(Module):
    """ An assembly is a container for multiple modules. This class is the base class for specific assemblies."""
    def __init__(self, parent:Composite, name:str):
        super().__init__(parent, name)
        self.connections:List[Connection] = []
        self.dummyConnections:List[Connection] = []
        self.unusedConnections:List[Connection] = []

    def checkForDoubleConnector(self, *connections: Connection) -> None:
        """ asserts if input or output connector is already used in another connection
        """
        for connection in connections:
            for existingConnection in chain(self.getConnections(recursive=True), self.getDummyConnections(recursive=True)):
                assert existingConnection.output != connection.output, \
                    f"Output connection [{connection.name}] in [{connection.parent.name}] conflicts with [{existingConnection.name}] in [{existingConnection.parent.name}] because they have the same output connector"
                
    
    def addConnection(self, connection:Connection):
        self.checkForDoubleConnector(connection)
        self.connections.append(connection)
        return connection
    
    def addDummyConnection(self, connection:Connection) -> Connection:
        self.checkForDoubleConnector(connection)
        self.dummyConnections.append(connection)
        return connection

    def addConnections(self, connections:Iterable[Connection]):
        self.checkForDoubleConnector(*connections)
        self.connections.extend(connections)
        return connections

# States

StateProbs = List[Tuple[List[InputStates], List[Prob]]] # for every input combination a probability list over all possible states

class State(Module):
    """ Represents a state in the domain. Note that we assume a "state" only depends on its
        inputs, not on previous states or outputs. 
    """
    def __init__(self, parent:Component, name:str):
        super().__init__(parent, name)
        self.state: Optional[Property] = None
        self.stateProbs: StateProbs = [] 
        self.normal: Optional[Normal] = None  # outputs based on state. Note: no failures

    def defineStates(self, *stateNames:str):
        self.state = Property(f"{self.name}States", stateNames)


# Development helpers

def printOverview(assembly: Assembly, verbose:bool=False) -> None:
    modules = list(assembly.getModules(recursive=True))
    if verbose:
        print(len(modules), "MODULES")
        for m in modules: print(m)
    connections = list(assembly.getConnections(recursive=True))
    connectorsUsed = list(connectors for connection in connections for connectors in connection.getConnectors())
    connectors = set(assembly.getConnectors(recursive=True))
    if verbose:
        print(len(connections), "CONNECTIONS")
        for c in connections: print(c)
    if verbose:
        print(len(connectors), "CONNECTORS")
        for c in connectors: print(c)
    if verbose:
        print(len(connectorsUsed), "CONNECTORS USED")
        for c in connectorsUsed: print(c)
    print("CONNECTORS NOT CONNECTED")
    for c in connectors - set(connectorsUsed) : print(c)
    print("INPUTS NOT CONNECTED")
    for input in assembly.openInputs(): print(input)
    print("CONNECTORS CONNECTED MULTIPLE TIMES")
    counter = Counter(connectorsUsed)
    for c, n in counter.items(): 
        if n>1: print(c, n)

if __name__ == "__main__":
    pass
