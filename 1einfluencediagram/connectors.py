from concepts import *

Moving = Property('Moving', 'YES NO')
class Movement(Modality):
    moving = Moving
class Shaft(Movement): pass
class DrivenShaft(Input, Shaft): pass
class DrivingShaft(Output, Shaft): pass

TriggerFired = Property('Fired', 'YES NO')
class Trigger(Modality):
    fired = TriggerFired
class TriggerConnector(Trigger): pass
class TriggerIn(Input, TriggerConnector): pass
class TriggerOut(Output, TriggerConnector): pass

PowerPresent = Property('Present', 'YES NO')
class Power(Modality):
    present = PowerPresent
class Plug(Power): pass
class InputPlug(Input, Plug): pass
class OutputPlug(Output, Plug): pass

AirPresent = Property('Present', 'YES NO')
class Air(Modality):
    present = AirPresent
class Hole(Air): pass
class AirInlet(Input, Hole): pass
class AirOutlet(Output, Hole): pass

SheetPresent = Property('Present', 'YES NO')
class Sheet(Modality):
    present = SheetPresent
class SheetHandler(Sheet): pass
class SheetIn(Input, SheetHandler): pass
class SheetOut(Output, SheetHandler): pass

ComputingPowerAvailable = Property('Available', 'YES NO')
class ComputingPower(Modality):
    available = ComputingPowerAvailable
class ComputingResource(ComputingPower) : pass
class ComputingSink(Input, ComputingResource): pass
class ComputingSource(Output, ComputingResource): pass

MessageShown = Property('Shown', 'YES NO')
class ErrorMessage(Modality):
    shown = MessageShown
class ErrorDisplay(Output, ErrorMessage): pass

IndicationVisible = Property('Indication', 'YES NO')
class Indication(Modality):
    visible = IndicationVisible
class Indicator(Output, Indication): pass

LightPresent = Property('Present', 'YES NO')
class Light(Modality):
    present = LightPresent
class LightPlug(Light): pass
class LightOut(Output, LightPlug): pass

WaterPresent = Property('Present', 'YES NO')
class Water(Modality):
    present = WaterPresent
class WaterPlug(Water): pass
class WaterInlet(Input, WaterPlug): pass
class WaterOutlet(Output, WaterPlug): pass


HeatLevel = Property('Level', 'LOW MEDIUM HIGH')
class Heat(Modality):
    level = HeatLevel
class HeatPlug(Heat): pass
class HeatIn(Input, HeatPlug): pass
class HeatOut(Output, HeatPlug): pass



FuelPresent = Property('Present', 'YES NO')
class Fuel(Modality):
    present = AirPresent
class FuelPlug(Fuel): pass
class FuelInlet(Input, FuelPlug): pass
class FuelOutlet(Output, FuelPlug): pass


Humidity = Property('Level', 'DRY MEDIUM WET')
class Moisture(Modality):
    level = Humidity
class MoisturePlug(Moisture): pass
class MoistureInlet(Input, MoisturePlug): pass
class MoistureOutlet(Output, MoisturePlug): pass

class MoistureSignalPlug(Moisture): pass
class MoistureSignalIn(Input, MoistureSignalPlug): pass
class MoistureSignalOut(Output, MoistureSignalPlug): pass

Present = Property('present', 'YES NO')
class IsPresent(Modality):
    present = Present
class Presence(Input, IsPresent) : pass
