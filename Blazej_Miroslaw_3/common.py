import pika

TRANSFER_TYPES = ["people", "cargo", "satellite"]

CARRIERS_REQUESTS_EXCHANGE = "carrier_requests"


def initialize_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.exchange_declare(
        exchange=CARRIERS_REQUESTS_EXCHANGE, exchange_type="direct"
    )

    return connection, channel
