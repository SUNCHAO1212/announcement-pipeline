# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

from pymongo import MongoClient

client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll_from = db.pledge
coll_to = db.pledge_filtered


def upload():
    i = 0
    for docu in coll_from.find({'title':{'$regex':'.*临时公告.*_股权质押公告$'}}):
        docu['content'] = docu['rawHtml']
        print(docu['title'])
        coll_to.save(docu)
        i += 1
        if i > 30:
            break


def show():
    for docu in coll_from.find({'crawOpt.secCode': {'$lt':'700000'}}):
        print(docu['crawOpt']['secName'], docu['crawOpt']['secCode'])


show()