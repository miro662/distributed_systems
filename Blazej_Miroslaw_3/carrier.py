import sys

import pika

from common import TRANSFER_TYPES, initialize_channel, CARRIERS_RESPONSES_FANOUT


class Carrier:
    def __init__(self, name, services):
        self._name = name
        self._services = services

        self._connection, self._channel = initialize_channel()
        queue_name = self._initialize_channel()
        self._bind_services(queue_name, services)

    def start(self):
        print(f"{self._name} carrier started operating")
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            print(f"{self._name} carrier stopped operating")

    def _handle_message(self, ch, method, properties, body):
        message = str(body, encoding="utf-8").split(";")
        if message[0] == "transfer_request":
            print(
                f"Recieved {method.routing_key} request from {message[1]}, id = {message[2]}"
            )
            confirmation_message = ("confirmation", message[2])
            self._channel.basic_publish(
                exchange=CARRIERS_RESPONSES_FANOUT,
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(
                    correlation_id=properties.correlation_id
                ),
                body=";".join(confirmation_message),
            )

    def _initialize_channel(self):
        result = self._channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        return queue_name

    def _bind_services(self, queue_name, services):
        for service in services:
            self._channel.basic_consume(
                queue=service, on_message_callback=self._handle_message, auto_ack=True
            )


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"usage: {sys.argv[0]} carrier_name transfer_types", file=sys.stderr)
        exit(1)

    carrier_name = sys.argv[1]
    transfer_types = set(sys.argv[2:])

    if len(transfer_types) != 2:
        print(f"Carrier has to handle 2 different services", file=sys.stderr)
        exit(1)

    for transfer_type in transfer_types:
        if transfer_type not in TRANSFER_TYPES:
            print(
                f'Unsupported transfer type: {transfer_type}. Supported choices: {"/".join(TRANSFER_TYPES)}',
                file=sys.stderr,
            )
            exit(1)

    carrier = Carrier(carrier_name, transfer_types)
    carrier.start()
