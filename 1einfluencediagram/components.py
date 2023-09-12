from concepts import *
from connectors import *
from connections import *


class Motor(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.signal = InputPlug(self, "power")
        self.shaft = DrivingShaft(self, "shaft")

        self.setNormal([([self.signal.present.YES] , [self.shaft.moving.YES]),
                        (ELSE                      , [self.shaft.moving.NO])])

        self.addFailure("broken", 0.005, [(ALWAYS, [self.shaft.moving.NO])])


class Fan(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.shaft = DrivenShaft(self, "shaft")
        self.outlet = AirOutlet(self, "air outlet")

        self.setNormal([([self.shaft.moving.YES] , [self.outlet.present.YES]),
                              (ELSE , [self.outlet.present.NO])])

if __name__ == "__main__":
    # Create a few components
#    AirSolenoidDriver(SYSTEM, "air solenoid driver")
#    CPU(SYSTEM, "cpu")
    pass