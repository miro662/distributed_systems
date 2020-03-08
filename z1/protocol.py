import socket
import threading
from enum import Enum


class MessageType(Enum):
    HELLO_SERVER = 0
    GENERAL_CLIENT = 1
    MESSAGE_CLIENT_TO_SERVER = 2
    MESSAGE_SERVER_TO_CLIENT = 3


class DisconnectedException(BaseException):
    pass


class Message:
    def __init__(self, message_type: MessageType, content: str = ""):
        self.message_type = message_type
        self.content = content

    def __repr__(self):
        return f'<Message: {self.message_type} "{self.content}">'

    def encode(self) -> bytes:
        mt = self.message_type.value.to_bytes(1, byteorder="big")
        content = self.content.encode(encoding="utf-8")
        cl = len(content).to_bytes(2, byteorder="big")
        return cl + mt + content

    @classmethod
    def decode(cls, data: bytes) -> "Message":
        mt = data[0]
        content = str(data[1:], encoding="utf-8")
        return cls(MessageType(mt), content)


class ProtocolSocket:
    def __init__(self, sock: socket.socket):
        self._socket = sock
        self._send_mutex = threading.RLock()
        self._recv_mutex = threading.RLock()

    def send(self, message: Message):
        message_bytes = message.encode()
        self._send_mutex.acquire()
        sent_total = 0
        while sent_total < len(message_bytes):
            try:
                sent = self._socket.send(message_bytes[sent_total:])
            except BrokenPipeError:
                raise DisconnectedException()
            if sent == 0:
                raise DisconnectedException()
            sent_total += sent
        self._send_mutex.release()

    def recv(self) -> Message:
        cl = int.from_bytes(self._recv_bytes(2), byteorder="big")
        message_bytes = self._recv_bytes(cl + 1)
        return Message.decode(message_bytes)

    def _recv_bytes(self, size: int) -> bytes:
        chunks = []
        self._recv_mutex.acquire()
        recv_total = 0
        while recv_total < size:
            chunk = self._socket.recv(size - recv_total)
            if chunk == b"":
                raise DisconnectedException()
            chunks.append(chunk)
            recv_total += len(chunk)
        self._recv_mutex.release()
        return b"".join(chunks)

    def close(self):
        self._socket.close()

    def fileno(self):
        return self._socket.fileno()


MAX_UDP_PACKET_SIZE = 4096
