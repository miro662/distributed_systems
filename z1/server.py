import functools
import threading
from typing import Tuple, Dict
import socket

from protocol import ProtocolSocket, DisconnectedException, MessageType, Message


class ServerClient:
    def __init__(
        self, client_socket: socket.socket, client_addr: Tuple[str, int], unregister
    ):
        self._thread: threading.Thread or None = None
        self._client_socket = ProtocolSocket(client_socket)
        self._client_addr = client_addr
        self._unregister = unregister
        self._nickname = "?"

    def handle(self):
        self._thread = threading.Thread(target=self._handle)
        self._thread.start()

    def _handle(self):
        try:
            self._initialize()
            self._handle_messages()
        except DisconnectedException:
            self._unregister()

    def _initialize(self):
        while True:
            hello_message = self._client_socket.recv()
            if hello_message.message_type == MessageType.HELLO_SERVER:
                break

        self._nickname = hello_message.content
        general_client_message = Message(MessageType.GENERAL_CLIENT)
        self._client_socket.send(general_client_message)

    def _handle_messages(self):
        while True:
            message = self._client_socket.recv()
            if message.message_type != MessageType.MESSAGE_CLIENT_TO_SERVER:
                continue

            message_with_nickname = f"[{self._nickname}] {message.content}"
            self._client_socket.send(
                Message(MessageType.MESSAGE_SERVER_TO_CLIENT, message_with_nickname)
            )


class ClientsList:
    def __init__(self):
        self._clients: Dict[int, ServerClient] = {}
        self._next_client_id = 0
        self._clients_list_mutex = threading.RLock()

    def __iter__(self):
        self._clients_list_mutex.acquire()
        for value in self._clients.values():
            yield value
        self._clients_list_mutex.release()

    def register_client(
        self, client_socket: socket.socket, client_addr: Tuple[str, int]
    ) -> ServerClient:
        unregister_function = functools.partial(
            self.unregister_client, self._next_client_id
        )
        server_client = ServerClient(client_socket, client_addr, unregister_function)

        self._clients_list_mutex.acquire()
        self._clients[self._next_client_id] = server_client
        self._next_client_id += 1
        self._clients_list_mutex.release()

        return server_client

    def unregister_client(self, client_id: int):
        self._clients_list_mutex.acquire()
        del self._clients[client_id]
        self._clients_list_mutex.release()


class Server:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clients = ClientsList()

    def listen(self, addr: Tuple[str, int]):
        self._socket.bind(addr)
        self._socket.listen()

        while True:
            client_socket, client_addr = self._socket.accept()
            server_client = self._clients.register_client(client_socket, client_addr)
            server_client.handle()


if __name__ == "__main__":
    server = Server()
    server.listen((socket.gethostname(), 2137))
