
from concepts import *
from connectors import *

class Wire(Connection): 
    def __init__(self, input: OutputPlug, output: InputPlug):
        super().__init__(input, output)

        self.setNormal([([self.input.present.YES] , [self.output.present.YES]),
                              ([self.input.present.NO] , [self.output.present.NO])])

        self.addFailure("Disconnected", 0.001, 
                               [([self.input.present.YES] , [self.output.present.NO]),
                                ([self.input.present.NO] , [self.output.present.NO])])

        self.addFailure("ShortToGround", 0.001,    # Special name, used in Bayes net generation
                               [([self.input.present.YES] , [self.output.present.NO]),
                                ([self.input.present.NO] , [self.output.present.NO])])


    def getDescriptor(self):
        return "wire"

class Axle(Connection): 
    def __init__(self, input: DrivingShaft, output: DrivenShaft):
        super().__init__(input, output)
    
        self.setNormal([([self.input.moving.YES], [self.output.moving.YES]),
                            (ELSE, [self.output.moving.NO])])

        self.addFailure("broken", 0.001, [(ALWAYS, [self.output.moving.NO])])


    def getDescriptor(self):
        return "axle" 


class WireRope(Connection): 
    def __init__(self, input: DrivingShaft, output: DrivenShaft):
        super().__init__(input, output)

        self.setNormal([([self.input.moving.YES], [self.output.moving.YES]),
                            (ELSE, [self.output.moving.NO])])

        self.addFailure("broken", 0.001, [(ALWAYS, [self.output.moving.NO])])
        self.addFailure("off pulley", 0.003, [(ALWAYS, [self.output.moving.NO])])


    def getDescriptor(self):
        return "wire rope" 

class SheetTransport(Connection[SheetOut,SheetIn]):
    def __init__(self, input: SheetOut, output: SheetIn):
        super().__init__(input, output)

        self.setNormal([([self.input.present.YES] , [self.output.present.YES]),
                             (ELSE , [self.output.present.NO])])

    def getDescriptor(self):
        return "sheet transport"

class TriggerConnection(Connection):
    def __init__(self, input: TriggerOut, output: TriggerIn):
        super().__init__(input, output)

        # always okay

    def getDescriptor(self):
        return "trigger connection"

class AirDuct(Connection):
    def __init__(self, input: AirOutlet, output: AirInlet):
        super().__init__(input, output)

        self.setNormal([([self.input.present.YES] , [self.output.present.YES]),
                              ([self.input.present.NO] , [self.output.present.NO])])

        self.addFailure("Leaking", 0.001, 
                           [([self.input.present.YES] , [self.output.present.NO]),
                            ([self.input.present.NO] , [self.output.present.NO])])

        self.addFailure("Blocked", 0.001, 
                           [([self.input.present.YES] , [self.output.present.NO]),
                            ([self.input.present.NO] , [self.output.present.NO])])


    def getDescriptor(self):
        return "air duct"

class Computing(Connection):
    def __init__(self, input:ComputingSource, output:ComputingSink):
        super().__init__(input, output)

        self.setNormal([([self.input.available.YES] , [self.output.available.YES]),
                              (ELSE , [self.output.available.NO])])

    def getDescriptor(self):
        return "computing power"

class Pipe(Connection):
    def __init__(self, input:WaterOutlet, output:WaterInlet):
        super().__init__(input, output)

        self.setNormal([([self.input.present.YES] , [self.output.present.YES]),
                              (ELSE , [self.output.present.NO])])

        self.addFailure("leaking", 0.001, [(ALWAYS, [self.output.present.NO])])


    def getDescriptor(self):
        return "pipe"

class HeatConductor(Connection):
    def __init__(self, input:HeatOut, output:HeatIn):
        super().__init__(input, output)

        self.setNormal([([self.input.level.HIGH] , [self.output.level.HIGH]),
                              ([self.input.level.MEDIUM] , [self.output.level.MEDIUM]),
                              ([self.input.level.LOW] , [self.output.level.LOW])])

        self.addFailure("leaking", 0.001,
                             [([self.input.level.HIGH] , [self.output.level.MEDIUM]),
                              ([self.input.level.MEDIUM] , [self.output.level.LOW]),
                              ([self.input.level.LOW] , [self.output.level.LOW])])
        
        self.addFailure("isolated", 0.001,
                             [([self.input.level.HIGH] , [self.output.level.LOW]),
                              ([self.input.level.MEDIUM] , [self.output.level.LOW]),
                              ([self.input.level.LOW] , [self.output.level.LOW])])


    def getDescriptor(self):
        return "conductor"

class Ability(Connection):
    def __init__(self, input:CapabilityOutput, output:CapabilityInput):
        super().__init__(input, output)

    def getDescriptor(self):
        return "ability"

if __name__ == "__main__":
    pass