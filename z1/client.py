import socket
import time
import threading
from typing import Tuple, Callable, List

from protocol import ProtocolSocket, Message, MessageType, DisconnectedException


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


class ClientObserver(threading.Thread):
    def __init__(
        self, client: Client, observers: List[Callable[[str], None]] or None = None
    ):
        super(ClientObserver, self).__init__()
        self._client = client
        self._observers = observers or []

    def run(self) -> None:
        while True:
            try:
                message = self._client.receive_message()
            except DisconnectedException:
                break

            for observer in self._observers:
                observer(message)


if __name__ == "__main__":
    client = Client()
    client.connect(("127.0.0.1", 2137), "miro662")

    client_observer = ClientObserver(client, [print])
    client_observer.start()

    while True:
        client.send_message("test")
        time.sleep(1)
