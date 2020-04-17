import sys

from common import TRANSFER_TYPES, CARRIERS_REQUESTS_EXCHANGE, initialize_channel


class Agency:
    def __init__(self, name):
        self._name = name
        self._last_request_id = 0
        self._channel = initialize_channel()

    def _next_request_id(self):
        request_id = self._last_request_id
        self._last_request_id += 1
        return request_id

    def request_transfer(self, transfer_type):
        assert transfer_type in TRANSFER_TYPES

        request_id = self._next_request_id()
        print(f"Requesting {transfer_type} transfer, id={request_id}")
        request = ("transfer_request", self._name, request_id)

        self._channel.basic_publish(
            exchange=CARRIERS_REQUESTS_EXCHANGE,
            routing_key=transfer_type,
            body=";".join(str(x) for x in request),
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} agency_name", file=sys.stderr)
        exit(1)

    agency = Agency(sys.argv[1])

    while True:
        try:
            command = input("> ").split(" ")
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
        else:
            print("Unknown command")
