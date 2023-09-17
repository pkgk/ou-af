from concepts import *
from connectors import *
from connections import *

class AirSplitter(Component): 
    def __init__(self, parent, name:str, nrOutlets:int):
        super().__init__(parent, name)
        self.inlet = AirInlet(self, "air inlet")
        self.outlets = [AirOutlet(self, f"outlet {nr+1}") for nr in range(nrOutlets)]

        self.setNormal([([self.inlet.present.YES], [self.outlets[nr].present.YES for nr in range(nrOutlets)]),
                                (ELSE, [self.outlets[nr].present.NO for nr in range(nrOutlets)])
        ])

        self.addFailure("Defect", 0.02, 
                        [(ALWAYS, [self.outlets[nr].present.NO for nr in range(nrOutlets)])])


class Solenoid(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.signal = InputPlug(self, "signal plug")
        self.shaft = DrivingShaft(self, "shaft")

        self.setNormal([([self.signal.present.YES] , [self.shaft.moving.YES]),
                              (ELSE , [self.shaft.moving.NO])])

class Motor(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.signal = InputPlug(self, "power")
        self.shaft = DrivingShaft(self, "shaft")

        self.setNormal([([self.signal.present.YES] , [self.shaft.moving.YES]),
                        (ELSE                      , [self.shaft.moving.NO])])

        self.addFailure("broken", 0.005, [(ALWAYS, [self.shaft.moving.NO])])


class Nozzle(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.inlet = AirInlet(self, "air inlet")
        self.sheetStill = SheetIn(self, "still sheet")
        self.sheetMoving = SheetOut(self, "moving sheet")

        self.setNormal([([self.inlet.present.YES, self.sheetStill.present.YES] , [self.sheetMoving.present.YES]),
                              (ELSE , [self.sheetMoving.present.NO])])
                            
        self.addFailure("clogged", 0.003, [(ALWAYS , [self.sheetMoving.present.NO])])


class Valve(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.shaft = DrivenShaft(self, "shaft")
        self.inlet = AirInlet(self, "air inlet")
        self.outlet = AirOutlet(self, "air outlet")

        self.setNormal([([self.shaft.moving.YES, self.inlet.present.YES] , [self.outlet.present.YES]),
                              (ELSE , [self.outlet.present.NO])])

class Fan(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.shaft = DrivenShaft(self, "shaft")
        self.outlet = AirOutlet(self, "air outlet")

        self.setNormal([([self.shaft.moving.YES] , [self.outlet.present.YES]),
                              (ELSE , [self.outlet.present.NO])])

class RotationSensor(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.shaft = DrivenShaft(self, "shaft")
        self.signal = OutputPlug(self, "signal plug")

        self.setNormal([([self.shaft.moving.YES] , [self.signal.present.YES]),
                             (ELSE , [self.signal.present.NO])])

        
class WireJoint(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.inputPlug = InputPlug(self, "input plug")
        self.outputPlug1 = OutputPlug(self, "output plug 1")
        self.outputPlug2 = OutputPlug(self, "output plug 2")

        self.setNormal([([self.inputPlug.present.YES] , [self.outputPlug1.present.YES, self.outputPlug2.present.YES]),
                              (ELSE , [self.outputPlug1.present.NO, self.outputPlug2.present.NO])])


class ErrorGenerator(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.board = ComputingSink(self, "computing resource")
        self.signal = InputPlug(self, "signal")

        self.error = ErrorDisplay(self, "error")

        # an error will be generated if board is functional and signal is on
        self.setNormal([([self.board.available.YES, self.signal.present.YES] , [self.error.shown.YES]),
                               (ELSE , [self.error.shown.NO])])

class ErrorGeneratorNegated(Component):
    """ Generates an error when there is no signal """
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.board = ComputingSink(self, "computing resource")
        self.signal = InputPlug(self, "signal")

        self.error = ErrorDisplay(self, "error")

        # an error will be generated if board is functional and signal is *NOT*
        self.setNormal([([self.board.available.YES, self.signal.present.NO] , [self.error.shown.YES]),
                               (ELSE , [self.error.shown.NO])])

class LogicAnd(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)
        self.input1 = InputPlug(self, "input 1")
        self.input2 = InputPlug(self, "input 2")
        self.output = OutputPlug(self, "output")

        # Never failing 'AND'-function on signals
        self.setNormal([([self.input1.present.YES, self.input2.present.YES], [self.output.present.YES]),
                               (ELSE , [self.output.present.NO])])



class AirSolenoidDriver(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.signal = ComputingSink(self, "signal")

        self.front = OutputPlug(self, "front")
        self.side = OutputPlug(self, "side")
        self.separation = OutputPlug(self, "separation")

        self.setNormal([([self.signal.available.YES] , [self.front.present.YES, self.side.present.NO, self.separation.present.NO]),
                               (ELSE , [self.front.present.NO, self.side.present.NO, self.separation.present.NO])])

        self.addFailure("no power", 0.00001, [(ALWAYS, [self.front.present.NO, self.side.present.NO, self.separation.present.NO])])



class Driver(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.signal = ComputingSink(self, "signal")
        self.powerOut = OutputPlug(self, "power out")

        self.setNormal([([self.signal.available.YES] , [self.powerOut.present.YES]),
                               (ELSE , [self.powerOut.present.NO])])

        self.addFailure("no power", 0.00001, [(ALWAYS, [self.powerOut.present.NO])])


        

class CPU(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.power = InputPlug(self, "mains plug")
        self.computingResource = ComputingSource(self, "computing power")

        self.setNormal([([self.power.present.YES] , [self.computingResource.available.YES]),
                               (ELSE , [self.computingResource.available.NO])])

        self.addFailure("broken", 0.00001, [(ALWAYS, [self.computingResource.available.NO])])




class PaperTouchSensor(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.sheet = SheetIn(self, "sheet")
        self.signal = OutputPlug(self, "signal")

        self.setNormal([([self.sheet.present.YES], [self.signal.present.YES]),
                                (ELSE , [self.signal.present.NO])])

        self.addFailure("No contact", 0.01, 
                                [(ALWAYS, [self.signal.present.NO])])



class TouchSensor(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.trigger = TriggerIn(self, "trigger")
        self.signal = OutputPlug(self, "signal")

        self.setNormal([([self.trigger.fired.YES], [self.signal.present.YES]),
                                (ELSE , [self.signal.present.NO])])

        self.addFailure("No contact", 0.0001, 
                                [(ALWAYS, [self.signal.present.NO])])



class RotationCounter(Component):
    def __init__(self, parent, name:str):
        super().__init__(parent, name)

        self.shaft = DrivenShaft(self, "shaft")
        self.signals = OutputPlug(self, "counting signals")

        self.setNormal([([self.shaft.moving.YES], [self.signals.present.YES]),
                                (ELSE, [self.signals.present.NO])])

        broken = [(ALWAYS, [self.signals.present.NO])]

        self.addFailure("sensor position 1 broken", 0.05, broken)
        self.addFailure("sensor position 2 broken", 0.05, broken)
        self.addFailure("pulse disk missing", 0.10, broken)

if __name__ == "__main__":
    # Create a few components
    AirSolenoidDriver(SYSTEM, "air solenoid driver")
    CPU(SYSTEM, "cpu")