from common import initialize_channel, CARRIERS_REQUESTS_FANOUT


def on_message(ch, method, properties, body):
    message = str(body, encoding="utf-8").split(";")
    if message[0] == "transfer_request":
        print(
            f"{method.routing_key} request from {message[1]}, id = {message[2]}"
        )
    if message[0] == "confirmation":
        print(
            f"Confirmation response, id = {message[1]}"
        )


if __name__ == '__main__':
    connection, channel = initialize_channel()

    result = channel.queue_declare(queue="", exclusive=True)
    callback_queue = result.method.queue

    channel.queue_bind(
        exchange=CARRIERS_REQUESTS_FANOUT,
        queue=callback_queue
    )
    channel.basic_consume(
        queue=callback_queue, on_message_callback=on_message, auto_ack=True
    )
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        pass
