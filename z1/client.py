import socket
import time
from typing import Tuple

from protocol import ProtocolSocket, Message, MessageType


class Client:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr: Tuple[str, int]):
        self._socket.connect(addr)


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 2138))
    s = ProtocolSocket(s)

    while True:
        s.send(Message(MessageType.HELLO_SERVER, "test message"))
        time.sleep(1)
