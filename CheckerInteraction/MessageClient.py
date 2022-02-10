import multiprocessing.connection
from multiprocessing.connection import Client, Listener
from typing import Tuple

from .Message import Message


class ConnectionHolder:
    def __init__(self):
        self.conn = None

    def send_message(self, message: Message):
        self.conn.send(message)

    def has_new_message(self):
        return self.conn.poll()

    def receive_message(self, timeout=0.0) -> Message:
        if not self.conn.poll(timeout):
            return Message(True, f'receive timeout ({timeout})s expired')
        return self.conn.recv()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()


class ClientBase(ConnectionHolder):
    def __init__(self):
        super().__init__()

    def connect_to_socket(self, address: Tuple[str, int]):
        self.conn = Client(address)


class ListenerBase(ConnectionHolder):
    def __init__(self):
        super().__init__()
        self.listener = Listener()

    def bind_socket(self, address: Tuple[str, int]):
        self.listener = Listener(address)

    def accept_connection(self):
        self.conn = self.listener.accept()
