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


AVAILABLE_TYPES = {
    'bulbulator': BulbulatorClient
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
