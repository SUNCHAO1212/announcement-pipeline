# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pika
from pymongo import MongoClient
import json
# ############################## 生产者 ##############################
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='192.168.1.251', port=5672
))
channel = connection.channel()
channel.queue_declare(queue='caitong-read-queue')  # 如果队列没有创建，就创建这个队列

client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll = db.jianchijihua
for document in coll.find():
    document['_id'] = str(document['_id'])
    document['rawId'] = document['_id']
    message = json.dumps(json.dumps(document, ensure_ascii=False))
    # message = document
    channel.basic_publish(exchange='',
                          routing_key='caitong-read-queue',   # 指定队列的关键字为，这里是队列的名字
                          body=message)  # 往队列里发的消息内容
    print(" [x] Sent %s" % message)
    input()

connection.close()