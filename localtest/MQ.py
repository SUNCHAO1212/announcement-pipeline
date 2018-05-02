# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika
import json

MQ_HOST2 = '120.55.180.243'
MQ_PORT2 = 5672
# MQ_HOST2 = '192.168.1.251'
# MQ_PORT2 = 5672
USER2 = 'guest'
PASSWORD2 = 'guest'
WRITE_QUEUE_NAME2 = 'hzguojian-info-queue'
EXCHANGE_NAME2 = 'hzguojian-info-exchange'
credentials2 = pika.PlainCredentials(USER2, PASSWORD2)
connection2 = pika.BlockingConnection(pika.ConnectionParameters(MQ_HOST2, MQ_PORT2, '/', credentials2))
channel_produce2 = connection2.channel()
channel_produce2.exchange_declare(exchange=EXCHANGE_NAME2, exchange_type='direct', durable=True,
                                  auto_delete=True)
channel_produce2.queue_declare(queue=WRITE_QUEUE_NAME2, durable=True)
channel_produce2.queue_bind(exchange=EXCHANGE_NAME2, queue=WRITE_QUEUE_NAME2)


def sent2mq(ee):
    channel_produce2.basic_publish(exchange='',
                                   routing_key=WRITE_QUEUE_NAME2,
                                   body=json.dumps(ee, ensure_ascii=False))
