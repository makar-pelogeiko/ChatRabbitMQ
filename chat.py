import pika
import threading
from threading import Lock
from datetime import datetime
import json


class Chat:
    def __init__(self, host_str='localhost', default_channel='default_channel'):
        self.host_str = host_str
        self.actual_channel = default_channel
        self.connections = dict()
        self.channels = dict()
        self.channel_buff = dict()
        self.mutexes = dict()
        self.receive_threads = dict()

        # For send
        # self.send_conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_str))
        # self.send_chnnl = self.send_conn.channel()
        # self.send_chnnl.exchange_declare(exchange='topic_logs', exchange_type='topic')
        # self.send_conn.close()

        self.user_name = "user_" + datetime.now().strftime("%m/%d/%Y_%H:%M:%S,%s")

        self.connections[self.actual_channel] = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_str))
        self.channels[self.actual_channel] = self.connections[self.actual_channel].channel()

        queue_name = self.user_name + '.' + self.actual_channel
        queue = self.channels[self.actual_channel].queue_declare(queue=queue_name, exclusive=True)
        self.channels[self.actual_channel].basic_consume(queue=queue_name, on_message_callback=self.callback,
                                                         auto_ack=True)
        self.channels[self.actual_channel].queue_bind(
            exchange='topic_logs', queue=queue.method.queue, routing_key='*.' + self.actual_channel)

        self.channel_buff[self.actual_channel] = []
        self.mutexes[self.actual_channel] = Lock()

        self.receive_threads[self.actual_channel] = threading.Thread(target=self.receive, args=(self.actual_channel,))
        self.receive_threads[self.actual_channel].start()

    def callback(self, ch, method, properties, body):
        if self.user_name == method.routing_key.split('.')[0]:
            # print("self message")
            return

        channel_name = method.routing_key.split('.')[1]
        if channel_name not in self.channel_buff.keys():
            print(f"unexpected channel name received: {method.routing_key}")
            return
        else:
            self.mutexes[channel_name].acquire()

            if (channel_name == self.actual_channel):
                if len(self.channel_buff[channel_name]) > 0:
                    self.channel_buff[channel_name].append(json.loads(body))

                else:
                    self.printer(json.loads(body))

            else:
                self.channel_buff[channel_name].append(json.loads(body))

            self.mutexes[channel_name].release()
        # print(" [x] Received %r" % json.loads(body))

    def switch_channel(self, channel_name: str):
        queue_name = self.user_name + '.' + channel_name
        self.actual_channel = channel_name

        if not (self.actual_channel in self.channel_buff.keys()):
            self.channel_buff[self.actual_channel] = []
            self.mutexes[self.actual_channel] = Lock()

            self.connections[self.actual_channel] = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host_str))
            self.channels[self.actual_channel] = self.connections[self.actual_channel].channel()

            queue = self.channels[self.actual_channel].queue_declare(queue=queue_name, exclusive=True)
            self.channels[self.actual_channel].basic_consume(queue=queue_name, on_message_callback=self.callback,
                                                             auto_ack=True)
            self.channels[self.actual_channel].queue_bind(
                exchange='topic_logs', queue=queue.method.queue, routing_key='*.' + self.actual_channel)

            self.receive_threads[self.actual_channel] = threading.Thread(target=self.receive,
                                                                         args=(self.actual_channel,))
            self.receive_threads[self.actual_channel].start()

        self.mutexes[self.actual_channel].acquire()
        print(f"-----Switched to [{self.actual_channel}]-----")
        self.write_all_from_channel(self.actual_channel)
        self.mutexes[self.actual_channel].release()

    def write_all_from_channel(self, channel_name):
        while len(self.channel_buff[channel_name]) > 0:
            message = self.channel_buff[channel_name].pop(0)
            self.printer(message)

    def send_msg(self, text: str):
        queue_name = self.user_name + '.' + self.actual_channel

        j_msg = dict()
        j_msg['text'] = text
        j_msg['user'] = self.user_name
        j_msg['channel'] = self.actual_channel
        # j_msg['time_send'] = datetime.now()

        self.send_conn = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_str))
        self.send_chnnl = self.send_conn.channel()
        self.send_chnnl.exchange_declare(exchange='topic_logs', exchange_type='topic')

        self.send_chnnl.basic_publish(exchange='topic_logs', routing_key=queue_name,
                                      body=json.dumps(j_msg),
                                      properties=pika.BasicProperties(
                                          delivery_mode=2,  # make message persistent
                                      ))
        self.send_conn.close()

    def receive(self, channel):
        # self.connection.ioloop.start()
        try:
            self.channels[channel].start_consuming()
        except:
            print(f"done with receiving {channel}")

    def dispose(self):
        # print("start disposing chat")
        for key in self.connections.keys():
            try:
                self.connections[key].close()
            except:
                pass
            self.receive_threads[key].join()
        # print("dispose done")

    def printer(self, message: dict):
        print(f"channel[{message['channel']}] user[{message['user']}]|  {message['text']}")

    def get_channel_lst(self, flag_show=True):
        result = list(self.channel_buff.keys())
        self.mutexes[self.actual_channel].acquire()
        print("available channels")
        print("name || number of messages")
        for item in result:
            print(f"{item} || {len(self.channel_buff[item])}")
        self.mutexes[self.actual_channel].release()
        return list(self.channel_buff.keys())
