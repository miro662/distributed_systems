import functools
import threading

from common import (
    initialize_channel,
    CARRIERS_REQUESTS_FANOUT,
    CARRIERS_RESPONSES_FANOUT,
    ADMIN_MESSAGES_EXCHANGE,
)

connection, channel = initialize_channel()


def on_message(ch, method, properties, body):
    message = str(body, encoding="utf-8").split(";")
    if message[0] == "transfer_request":
        print(f"{method.routing_key} request from {message[1]}, id = {message[2]}")
    if message[0] == "confirmation":
        print(f"Confirmation response, id = {message[1]}")


def handle_commands():
    while True:
        command = input()
        split_command = command.split(" ")
        topic, message_content = (split_command[0], " ".join(split_command[1:]))
        message = ("admin", message_content)

        connection.add_callback_threadsafe(
            functools.partial(
                channel.basic_publish,
                exchange=ADMIN_MESSAGES_EXCHANGE,
                routing_key=topic,
                body=";".join(str(x) for x in message),
            )
        )


if __name__ == "__main__":
    result = channel.queue_declare(queue="", exclusive=True)
    callback_queue = result.method.queue

    channel.queue_bind(exchange=CARRIERS_REQUESTS_FANOUT, queue=callback_queue)
    channel.queue_bind(exchange=CARRIERS_RESPONSES_FANOUT, queue=callback_queue)
    channel.basic_consume(
        queue=callback_queue, on_message_callback=on_message, auto_ack=True
    )

    commands_thread = threading.Thread(target=channel.start_consuming)
    commands_thread.start()

    handle_commands()
