import sys, Ice
import SmartHouse


class BulbulatorClient:
    COMMANDS = {}

    @classmethod
    def command(cls, command):
        cls.COMMANDS[command.__name__] = command
        return command

    def __init__(self, communicator, name):
        self._name = name
        base = communicator.stringToProxy(f"{name}:default -p 10000")
        self._stub = SmartHouse.BulbulatorPrx.checkedCast(base)

    def interact(self):
        while True:
            print(f'{self._name}> ', end='')
            command_name = input()
            if command_name in self.COMMANDS.keys():
                self.COMMANDS[command_name](self)
            elif command_name == 'exit':
                return
            else:
                print('Invaild command, use help for commands list')


@BulbulatorClient.command
def help(self):
    print(f"Available commands: {', '. join(self.COMMANDS)}, exit")


@BulbulatorClient.command
def mumble(self):
    self._stub.mumble()


with Ice.initialize(sys.argv) as communicator:
    client = BulbulatorClient(communicator, "Bulbulator1")
    client.interact()
    base = communicator.stringToProxy("Bulbulator1:default -p 10000")
    bulbulator = SmartHouse.BulbulatorPrx.checkedCast(base)
    if not bulbulator:
        raise RuntimeError("Invaild proxy")

    bulbulator.mumble()