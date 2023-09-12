from concepts import *
from connectors import *



class Axle(Connection): 
    def __init__(self, input: DrivingShaft, output: DrivenShaft):
        super().__init__(input, output)
    
        self.setNormal([([self.input.moving.YES], [self.output.moving.YES]),
                            (ELSE, [self.output.moving.NO])])

        self.addFailure("broken", 0.001, [(ALWAYS, [self.output.moving.NO])])


    def getDescriptor(self):
        return "axle" 

class Ability(Connection):
    def __init__(self, input:CapabilityOutput, output:CapabilityInput):
        super().__init__(input, output)

    def getDescriptor(self):
        return "ability"

if __name__ == "__main__":
    pass

