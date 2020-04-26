import sys, Ice
import SmartHouse


class Client:
    COMMANDS = {}

    @classmethod
    def command(cls, command):
        cls.COMMANDS[command.__name__] = command
        return command

    def __init__(self, communicator, name):
        self._name = name
        base = communicator.stringToProxy(f"{name}:default -p 10000")
        self._stub = self.get_stub(base)

    def interact(self):
        while True:
            print(f'{self._name}> ', end='')
            try:
                command_name = input()
            except KeyboardInterrupt:
                break
            if command_name in self.COMMANDS.keys():
                self.COMMANDS[command_name](self)
            elif command_name == 'exit':
                return
            else:
                print('Invaild command, use help for commands list')


@Client.command
def help(self):
    print(f"Available commands: {', '. join(self.COMMANDS)}, exit")


class BulbulatorClient(Client):
    def get_stub(self, base):
        return SmartHouse.BulbulatorPrx.checkedCast(base)


@BulbulatorClient.command
def mumble(self):
    print(self._stub.mumble())


class ThermometerClient(Client):
    def get_stub(self, base):
        return SmartHouse.ThermometerPrx.checkedCast(base)
    

@ThermometerClient.command
def temperature(self):
    print(f"temperatue: {self._stub.getTemperature()}")


@ThermometerClient.command
def range(self):
    temp_range = self._stub.getSuportedRange()
    print(f"from {temp_range.min} to {temp_range.max}")


class LightBulbClient(Client):
    def get_stub(self, base):
        return SmartHouse.LightBulbPrx.checkedCast(base)


@LightBulbClient.command
def get_state(self):
    print("on" if self._stub.getState() else "off")


@LightBulbClient.command
def set_state(self):
    answer = input("New state [on/off]: ")
    self._stub.setState(answer == 'on')


class RGBBulbClient(LightBulbClient):
    def get_stub(self, base):
        return SmartHouse.RGBBulbPrx.checkedCast(base)


@RGBBulbClient.command
def get_color(self):
    color = self._stub.getColor()
    print(f"r: {color.r}, g: {color.g}, b: {color.b}")


@RGBBulbClient.command
def set_color(self):
    color = SmartHouse.Color()
    color.r = float(input("r: "))
    color.g = float(input("g: "))
    color.b = float(input("b: "))
    try:
        self._stub.setColor(color)
    except SmartHouse.InvaildColorException:
        print("Invaild color")


class StroboscopeBulbClient(LightBulbClient):
    def get_stub(self, base):
        return SmartHouse.StroboscopeBulbPrx.checkedCast(base)


@StroboscopeBulbClient.command
def set_frequency(self):
    new_frequency = float(input("new frequency: "))
    try:
        self._stub.setFrequency(new_frequency)
    except SmartHouse.UnsupportedFrequency:
        print("Unsupported frequency")


@StroboscopeBulbClient.command
def get_frequency(self):
    print(f"frequency: {self._stub.getFrequency()}")


@StroboscopeBulbClient.command
def supported_range(self):
    freq_range = self._stub.getSupportedFrequenciesRange()
    print(f"from {freq_range.min} to {freq_range.max}")


@StroboscopeBulbClient.command
def set_mode(self):
    new_mode_str = input("new mode [blink/sine/still]: ")
    MODES = {
        'blink': SmartHouse.Mode.Blink,
        'sine': SmartHouse.Mode.Sine,
        'still': SmartHouse.Mode.Still,
    }
    new_mode = MODES.get(new_mode_str)
    if new_mode:
        self._stub.setMode(new_mode)
    else:
        print(f"unsupported mode: {new_mode_str}")


AVAILABLE_TYPES = {
    'bulbulator': BulbulatorClient,
    'thermometer': ThermometerClient,
    'lightbulb': LightBulbClient,
    'rgbbulb': RGBBulbClient,
    'stroboscopebulb': StroboscopeBulbClient
}

if __name__ == '__main__':
    with Ice.initialize(sys.argv) as communicator:
        while True:
            print('> ', end='')
            try:
                command = input()
            except KeyboardInterrupt:
                break

            split_command = command.rstrip().split(' ')
            if split_command[0] == 'help':
                print('syntax: <type> <name>')
            elif split_command[0] == 'exit':
                break
            elif len(split_command) == 2:
                client_class = AVAILABLE_TYPES.get(split_command[0])
                if client_class is None:
                    print(f'Unknown type: {split_command[0]}, available types: {", ".join(AVAILABLE_TYPES.keys())}')
                    continue
                
                try:
                    client = client_class(communicator, split_command[1])
                    client.interact()
                except Ice.ObjectNotExistException:
                    print(f"Object {split_command[1]} does not exist")
            else:
                print(f'Invaild command: {split_command[0]}')
