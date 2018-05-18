# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

from pymongo import MongoClient

client = MongoClient(host='192.168.1.251', port=27017)
db = client.SecurityAnnouncement
coll_from = db.test2

data = {}
for docu in db.test2.find({'title':{'$regex':'^.*增持.*计划的?公告$'}}):
    try:
        if docu['crawOpt']['secName'] in data:
            data[docu['crawOpt']['secName']] += 1
        else:
            data[docu['crawOpt']['secName']] = 1
    except Exception as e:
        pass


for k in data:
    if data[k] > 1:
        print(k,data[k])
input()