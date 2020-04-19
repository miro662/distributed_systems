import functools
import sys
from threading import Thread

import pika

from common import TRANSFER_TYPES, CARRIERS_REQUESTS_EXCHANGE, initialize_channel, CARRIERS_REQUESTS_FANOUT


class Agency:
    def __init__(self, name):
        self._name = name
        self._last_request_id = 0
        self._connection, self._channel = initialize_channel()
        self._callback_queue = self._initialize_callback_queue()

    def _next_request_id(self):
        request_id = self._last_request_id
        self._last_request_id += 1
        return request_id

    def request_transfer(self, transfer_type):
        assert transfer_type in TRANSFER_TYPES

        request_id = self._next_request_id()
        print(f"Requesting {transfer_type} transfer, id={request_id}")
        request = ("transfer_request", self._name, request_id)

        self._connection.add_callback_threadsafe(
            functools.partial(
                self._channel.basic_publish,
                exchange=CARRIERS_REQUESTS_FANOUT,
                routing_key=transfer_type,
                properties=pika.BasicProperties(
                    reply_to=self._callback_queue, correlation_id=str(request_id)
                ),
                body=";".join(str(x) for x in request),
            )
        )

    def start(self):
        print(f"{self._name} agency started operating")
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            print(f"{self._name} agency stopped operating")

    def _handle_message(self, ch, method, properties, body):
        message = str(body, encoding="utf-8").split(";")
        if message[0] == "confirmation":
            print(f"Recieved confirmation of transfer, id = {message[1]}")

    def _initialize_callback_queue(self):
        result = self._channel.queue_declare(queue="", exclusive=True)
        callback_queue = result.method.queue

        self._channel.queue_bind(
            exchange=CARRIERS_REQUESTS_EXCHANGE,
            queue=callback_queue,
            routing_key=callback_queue,
        )

        self._channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self._handle_message,
            auto_ack=True,
        )
        return callback_queue


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} agency_name", file=sys.stderr)
        exit(1)

    agency = Agency(sys.argv[1])
    notifications_thread = Thread(target=agency.start)
    notifications_thread.start()

    while True:
        try:
            command = input("").split(" ")
        except KeyboardInterrupt:
            break

        if command[0] == "help":
            print(
                f"""help - displays available commands
request [{'/'.join(TRANSFER_TYPES)}] - requests transfer
exit - exits from program"""
            )
        elif command[0] == "exit":
            break
        elif command[0] == "request":
            if command[1] not in TRANSFER_TYPES:
                print(f"Unsupported transfer type: {command[1]}")
            else:
                agency.request_transfer(command[1])
        elif command[0] == "":
            pass
        else:
            print("Unknown command")
