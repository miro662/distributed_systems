import socket
from typing import Tuple


class Client:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr: Tuple[str, int]):
        self._socket.connect(addr)


if __name__ == "__main__":
    client = Client()
    client.connect(("127.0.0.1", 2138))
