# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

from pymongo import MongoClient

client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll_from = db.test2
coll_to = db.jianchijieguo
for docu in coll_from.find({'title':{'$regex':'.*减持.*结果的?公告'}}):
    docu['content'] = docu['rawHtml']
    print(docu['title'])
    # for key in docu:
    #     print(key)
    # coll_to.save(docu)


