from concepts import *
from components import *
#from bayesgen import *
#import viz

class Blades(Component):
    def __init__(self, parent, name):
        super().__init__(parent, name)

        self.shaft = DrivenShaft(self, "shaft")
        self.air = AirOutlet(self, "air outlet")

        self.setNormal([([self.shaft.moving.YES] , [self.air.present.YES]),
                        (ELSE                    , [self.air.present.NO])])

        self.addFailure("broken", 0.002, [(ALWAYS, [self.air.present.NO])])



class Fan(Assembly):
    def __init__(self, parent, name):
        super().__init__(parent, name)

        self.motor = Motor(self, "Motor")
        self.blades = Blades(self, "Blades")

        self.c1 = self.addConnection(Axle(self.motor.shaft, self.blades.shaft))


if __name__ == "__main__":

    fan = Fan(SYSTEM, "Fan")
    printOverview(fan)


#    viz.writeGraph(fan, alwaysShowConnectionNodes=True)
#    bayesgen.writeNetwork(fan)
#    print(fan.blades.normal.relation)
#    print(fan.blades.failures[0].name)
#    print(fan.blades.failures[0].name)

