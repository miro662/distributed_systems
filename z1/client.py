import select
import socket
import sys
from typing import Tuple

from protocol import ProtocolSocket, Message, MessageType, DisconnectedException


class ClientProtocolWrapper:
    def __init__(self, sock):
        self._socket = sock
        self._protocol_socket = ProtocolSocket(self._socket)

    def send_message(self, message: str):
        message = Message(MessageType.MESSAGE_CLIENT_TO_SERVER, message)
        self._protocol_socket.send(message)

    def receive_message(self) -> str:
        while True:
            message = self._protocol_socket.recv()
            if message.message_type != MessageType.MESSAGE_SERVER_TO_CLIENT:
                continue

            return message.content


class Client:
    def __init__(self, ascii_art):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._protocol_socket = ProtocolSocket(self._socket)
        self._protocol_wrapper = ClientProtocolWrapper(self._socket)
        self._ascii_art = bytes(ascii_art, encoding='utf-8')
        self.nickname = "?"

    def connect(self, addr: Tuple[str, int], nickname: str):
        self._socket.connect(addr)

        tcp_socket_addr = self._socket.getsockname()
        self._udp_socket.bind(tcp_socket_addr)
        self._udp_socket.connect(addr)

        self.nickname = nickname
        self._initialize(nickname)

    @property
    def socket(self):
        return self._socket

    @property
    def udp_socket(self):
        return self._udp_socket

    def send_message(self, message: str):
        self._protocol_wrapper.send_message(message)

    def receive_message(self) -> str:
        return self._protocol_wrapper.receive_message()

    def send_ascii_art(self):
        self._udp_socket.send(self._ascii_art)

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


class ClientUI:
    def __init__(self, client):
        self._client = client

    def main(self):
        self._prompt()
        while True:
            read_sockets = [self._client.socket, self._client.udp_socket, sys.stdin]
            r, w, e = select.select(read_sockets, [], [])
            for s in r:
                if s == self._client.socket:
                    self._print_message_from(s)
                if s == self._client.udp_socket:
                    self._print_message_from_udp(s)
                else:
                    self._read_and_send_message()

    def _print_message_from(self, sock):
        wrapper = ClientProtocolWrapper(sock)
        sys.stdout.write('\r')
        message = wrapper.receive_message()
        sys.stdout.write(message + "\n")
        self._prompt()

    def _print_message_from_udp(self, sock):
        sys.stdout.write('\r')
        message, _ = sock.recvfrom(4096)
        message_str = str(message, encoding='utf-8')
        sys.stdout.write(message_str + "\n")
        self._prompt()

    def _read_and_send_message(self):
        message = sys.stdin.readline().rstrip()
        if message == 'U':
            self._client.send_ascii_art()
        else:
            self._client.send_message(message)
        self._prompt()

    def _prompt(self):
        sys.stdout.write(f'[{self._client.nickname}] ')
        sys.stdout.flush()


if __name__ == "__main__":
    with open('asciiart.txt', 'r') as f:
        asciiart = ''.join(f.readlines())

    print(asciiart)

    if len(sys.argv) != 3:
        print(f'usage: {sys.argv[0]} ip port', file=sys.stderr)
        sys.exit(1)
    program_name, ip, port_str = sys.argv
    nickname = input('Nickname: ')

    client = Client(asciiart)
    client.connect((ip, int(port_str)), nickname)

    ui = ClientUI(client)
    try:
        ui.main()
    except DisconnectedException:
        print("Server closed")
        sys.exit(1)

