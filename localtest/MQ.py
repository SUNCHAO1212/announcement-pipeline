# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika
import json
from pipeline import pipeline
from localtest.mysql import update_mysql


MQ_IN_HOST = '192.168.1.251'
MQ_IN_PORT = 5672
MQ_OUT_HOST = '192.168.1.251'
MQ_OUT_PORT = 5672
USER = 'guest'
PASSWORD = 'guest'
WRITE_QUEUE_NAME = 'dev-supermind-knowledge-queue'
READ_QUEUE_NAME = 'caitong-read-queue'
# EXCHANGE_NAME = 'dev-supermind-exchange'
credentials = pika.PlainCredentials(USER, PASSWORD)
#
update_mysql()
# sender
channel_producer = pika.BlockingConnection(pika.ConnectionParameters(MQ_OUT_HOST, MQ_OUT_PORT, '/', credentials))
channel_producer = channel_producer.channel()
channel_producer.queue_declare(queue=WRITE_QUEUE_NAME, durable=True)


def sent2mq(ee):
    # ee=json.dumps(ee, ensure_ascii=False)
    print(" [x] Sent %s" % ee)
    channel_producer.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE_NAME,
                                   body=ee)


# receiver
connection_consumer = pika.BlockingConnection(pika.ConnectionParameters(MQ_IN_HOST, MQ_IN_PORT, '/', credentials))
channel_consumer = connection_consumer.channel()
channel_consumer.queue_declare(queue=READ_QUEUE_NAME)


def callback(ch, method, propertities,body):
    if isinstance(body, bytes):
        body = body.decode()
    print(" [x] Received %r" % body)
    body = pipeline(body)
    if body:
        sent2mq(body)
    else:
        print('Knowledge not extracted.')


channel_consumer.basic_consume(callback,
                      queue=READ_QUEUE_NAME,  # 队列名
                      no_ack=True)  # 不通知已经收到，如果连接中断可能消息丢失
print(' [*] Waiting for message. To exit press CTRL+C')
channel_consumer.start_consuming()


