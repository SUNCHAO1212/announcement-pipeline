# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika

# ########################### 消费者 ###########################

connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='192.168.1.251', port=5672))
channel = connection.channel()

channel.queue_declare(queue='local-supermind-knowledge-queue', durable=True)  # 如果队列没有创建，就创建这个队列


def callback(ch, method, propertities,body):
    if type(body) == bytes:
        body = body.decode()
    print(" [x] Received %r" % body)


channel.basic_consume(callback,
                      queue='local-supermind-knowledge-queue',  # 队列名
                      no_ack=True)  # 不通知已经收到，如果连接中断可能消息丢失

print(' [*] Waiting for message. To exit press CTRL+C')
channel.start_consuming()