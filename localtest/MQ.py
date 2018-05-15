# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika
from localtest.pipeline import pipeline
from localtest.mysql import get_mysql_queues


MQ_HOST = '192.168.1.251'
MQ_PORT = 5672
USER = 'guest'
PASSWORD = 'guest'
credentials = pika.PlainCredentials(USER, PASSWORD)

# 更新SQL时间，获得队列名
queues_dict = get_mysql_queues()
if queues_dict:
    WRITE_QUEUE_NAME = queues_dict['write']
    READ_QUEUE_NAME = queues_dict['read']
    EXCHANGE_NAME = queues_dict['exchange']
else:
    WRITE_QUEUE_NAME = 'local-supermind-knowledge-queue'
    READ_QUEUE_NAME = 'caitong-read-queue'
    EXCHANGE_NAME = 'local-supermind-exchange'

# producer
channel_producer = pika.BlockingConnection(pika.ConnectionParameters(MQ_HOST, MQ_PORT, '/', credentials))
channel_producer = channel_producer.channel()
channel_producer.queue_declare(queue='local-supermind-knowledge-queue', durable=True)


def sent2mq(ee):
    # ee=json.dumps(ee, ensure_ascii=False)
    print(" [x] Sent %s" % ee)
    channel_producer.basic_publish(exchange='',
                                   routing_key='local-supermind-knowledge-queue',
                                   body=ee)


# consumer
connection_consumer = pika.BlockingConnection(pika.ConnectionParameters(MQ_HOST, MQ_PORT, '/', credentials))
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


