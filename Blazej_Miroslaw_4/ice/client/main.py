import sys, Ice
import SmartHouse

with Ice.initialize(sys.argv) as communicator:
    base = communicator.stringToProxy("Bulbulator1:default -p 10000")
    bulbulator = SmartHouse.BulbulatorPrx.checkedCast(base)
    if not bulbulator:
        raise RuntimeError("Invaild proxy")

    bulbulator.mumble()