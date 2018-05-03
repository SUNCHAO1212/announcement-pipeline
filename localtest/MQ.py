# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika
import json

MQ_IN_HOST = '192.168.1.251'
MQ_IN_PORT = 5672
MQ_OUT_HOST = '192.168.1.251'
MQ_OUT_PORT = 5672
USER = 'guest'
PASSWORD = 'guest'
WRITE_QUEUE_NAME = 'caitong-write-queue'
READ_QUEUE_NAME = 'caitong-read-queue'
credentials = pika.PlainCredentials(USER, PASSWORD)
# sender
connection_sender = pika.BlockingConnection(pika.ConnectionParameters(MQ_OUT_HOST, MQ_OUT_PORT, '/', credentials))
channel_sender = connection_sender.channel()
channel_sender.queue_declare(queue=WRITE_QUEUE_NAME)

def sent2mq(ee):
    # ee=json.dumps(ee, ensure_ascii=False)
    channel_sender.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE_NAME,
                                   body=ee)


# receiver
connection_receiver = pika.BlockingConnection(pika.ConnectionParameters(MQ_IN_HOST, MQ_IN_PORT, '/', credentials))
channel_receiver = connection_receiver.channel()
channel_receiver.queue_declare(queue=READ_QUEUE_NAME)


def callback(ch, method, propertities,body):
    print(" [x] Received %r" % body)
    sent2mq(body)


channel_receiver.basic_consume(callback,
                      queue=READ_QUEUE_NAME,  # 队列名
                      no_ack=True)  # 不通知已经收到，如果连接中断可能消息丢失
print(' [*] Waiting for message. To exit press CTRL+C')
channel_receiver.start_consuming()



