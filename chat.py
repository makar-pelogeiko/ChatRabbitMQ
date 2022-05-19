import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

def create_connection(host_str='localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_str))
    channel = connection.channel()
    return channel

def switch_channel(channel, channel_name, callback):
    channel.queue_declare(queue=channel_name)
    channel.basic_consume(queue=channel_name, on_message_callback=callback, auto_ack=True)