import socket
import string
import time
import random
from typing import Tuple

from protocol import ProtocolSocket, Message, MessageType


class Client:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr: Tuple[str, int]):
        self._socket.connect(addr)


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 2137))
    s = ProtocolSocket(s)
    s.send(
        Message(
            MessageType.HELLO_SERVER,
            "".join(random.choice(string.ascii_lowercase) for _ in range(16)),
        )
    )
    msg = s.recv()
    assert msg.message_type == MessageType.GENERAL_CLIENT
    while True:
        time.sleep(1)
        s.send(Message(MessageType.MESSAGE_CLIENT_TO_SERVER, "test message"))
        msg = s.recv()
        print(msg.content)
