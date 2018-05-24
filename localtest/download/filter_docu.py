# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from pymongo import MongoClient

client = MongoClient(host='192.168.1.251', port=27017)
db = client.SecurityAnnouncement
coll_from = db.test2
coll_to = db.jianchijihua

for i, document in enumerate(coll_from.find({'crawOpt.secCode':'300379', 'title':{'$regex':'.*减持计划的公告$'}})):
    print(i, document['title'])
    coll_to.save(document)
