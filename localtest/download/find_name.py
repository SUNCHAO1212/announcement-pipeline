# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

from pymongo import MongoClient

client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll_from = db.pledge
coll_to = db.pledge_filtered


def show():
    data = {}
    for docu in coll_from.find({'crawOpt.secCode': {'$lt':'700000'}}):
        # print(docu['crawOpt']['secName'], docu['crawOpt']['secCode'])
        try:
            if docu['crawOpt']['secName'] in data:
                data[docu['crawOpt']['secName']] += 1
            else:
                data[docu['crawOpt']['secName']] = 1
        except Exception as e:
            print(e)
            pass

    for k in data:
        if data[k] > 1:
            print(k, data[k])
    sorted_data = sorted(data.items(), key=lambda d: d[1], reverse=True)
    print(sorted_data)
    input()

show()


