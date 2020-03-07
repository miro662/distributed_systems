import socket
import time
from typing import Tuple

from protocol import ProtocolSocket, Message, MessageType


class Client:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._protocol_socket = ProtocolSocket(self._socket)

    def connect(self, addr: Tuple[str, int], nickname: str):
        self._socket.connect(addr)
        self._initialize(nickname)

    def send_message(self, message: str):
        message = Message(MessageType.MESSAGE_CLIENT_TO_SERVER, message)
        self._protocol_socket.send(message)

    def receive_message(self) -> str:
        while True:
            message = self._protocol_socket.recv()
            if message.message_type != MessageType.MESSAGE_SERVER_TO_CLIENT:
                continue

            return message.content

    def _initialize(self, nickname: str):
        self._send_hello_server_message(nickname)
        self._wait_for_general_client_message()

    def _send_hello_server_message(self, nickname: str):
        self._protocol_socket.send(Message(MessageType.HELLO_SERVER, nickname))

    def _wait_for_general_client_message(self):
        while True:
            message = self._protocol_socket.recv()
            if message.message_type == MessageType.GENERAL_CLIENT:
                break


if __name__ == "__main__":
    client = Client()
    client.connect(("127.0.0.1", 2137), "miro662")
    while True:
        client.send_message("test")
        print(client.receive_message())
        time.sleep(1)
