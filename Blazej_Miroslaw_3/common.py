import pika

TRANSFER_TYPES = ["people", "cargo", "satellite"]

CARRIERS_REQUESTS_EXCHANGE = "carrier_requests"


def initialize_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.exchange_declare(
        exchange=CARRIERS_REQUESTS_EXCHANGE, exchange_type="direct"
    )

    for transfer_type in TRANSFER_TYPES:
        channel.queue_declare(queue=transfer_type, durable=True)
        channel.queue_bind(
            exchange=CARRIERS_REQUESTS_EXCHANGE,
            queue=transfer_type,
            routing_key=transfer_type,
        )
        channel.basic_qos(prefetch_count=1)

    return connection, channel
