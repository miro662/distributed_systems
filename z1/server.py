import functools
import logging
import select
import sys
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Tuple, Dict, Callable, List
import socket

from protocol import ProtocolSocket, DisconnectedException, MessageType, Message, MAX_UDP_PACKET_SIZE

logging.basicConfig(level=logging.DEBUG)


class ServerClient:
    def __init__(
        self,
        client_socket: socket.socket,
        client_addr: Tuple[str, int],
        unregister: Callable,
        send_message_to_all: Callable[[str, List['ServerClient']], None]
    ):
        self._client_socket = ProtocolSocket(client_socket)
        self.client_addr = client_addr
        self._unregister = unregister
        self._nickname = "?"
        self._send_message_to_all = send_message_to_all

    def handle(self):
        try:
            self._initialize()
            self._handle_messages()
        except DisconnectedException:
            logging.debug(f"{self._nickname} disconnected")
            self._unregister()

    def _initialize(self):
        while True:
            hello_message = self._client_socket.recv()
            if hello_message.message_type == MessageType.HELLO_SERVER:
                break

        self._nickname = hello_message.content
        logging.debug(
            f"receivied hello message from {self.client_addr}, nickname: {self._nickname}"
        )

        general_client_message = Message(MessageType.GENERAL_CLIENT)
        self._client_socket.send(general_client_message)

    def _handle_messages(self):
        while True:
            message = self._client_socket.recv()
            if message.message_type != MessageType.MESSAGE_CLIENT_TO_SERVER:
                continue

            message = message.content
            logging.debug(f'message from {self._nickname}: "{message}"')
            message_with_nickname = f"[{self._nickname}] {message}"

            self._send_message_to_all(message_with_nickname, [self])

    def send_message(self, message):
        self._client_socket.send(
            Message(MessageType.MESSAGE_SERVER_TO_CLIENT, message)
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
        server_client = ServerClient(client_socket, client_addr, unregister_function, self.send_message_to_all)

        self._clients_list_mutex.acquire()
        self._clients[self._next_client_id] = server_client
        self._next_client_id += 1
        self._clients_list_mutex.release()

        return server_client

    def unregister_client(self, client_id: int):
        self._clients_list_mutex.acquire()
        del self._clients[client_id]
        self._clients_list_mutex.release()

    def send_message_to_all(self, message: str, do_not_send_to: List[ServerClient] = None):
        for client in self._clients.values():
            if do_not_send_to is None or client not in do_not_send_to:
                client.send_message(message)


class Server:
    def __init__(self):
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._clients = ClientsList()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)

    def listen(self, addr: Tuple[str, int]):
        self._tcp_socket.bind(addr)
        self._udp_socket.bind(addr)
        self._tcp_socket.listen()
        logging.debug(f"listening on {addr}")

        while True:
            r, w, e = select.select([self._tcp_socket, self._udp_socket], [], [])
            for sock in r:
                if sock == self._tcp_socket:
                    self._handle_tcp_connection(sock)
                else:
                    self._handle_udp(sock)

    def _handle_udp(self, sock):
        logging.debug('received UDP packet')
        ascii_art, addr = sock.recvfrom(MAX_UDP_PACKET_SIZE)
        for client in self._clients:
            if addr != client.client_addr:
                sock.sendto(ascii_art, client.client_addr)

    def _handle_tcp_connection(self, sock):
        client_socket, client_addr = sock.accept()
        logging.debug(f"accepting connection from {client_addr}")
        server_client = self._clients.register_client(client_socket, client_addr)
        self._thread_pool.submit(server_client.handle)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'usage: {sys.argv[0]} ip port', file=sys.stderr)
        sys.exit(1)
    program_name, ip, port_str = sys.argv

    server = Server()
    server.listen((ip, int(port_str)))
