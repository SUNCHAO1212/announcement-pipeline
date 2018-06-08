# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from pymongo import MongoClient

client = MongoClient(host='192.168.1.251', port=27017)
db = client.SecurityAnnouncement
coll_from = db.pledge
coll_to = db.pledge_filtered

for i, document in enumerate(coll_from.find({'crawOpt.secName':'信邦制药', 'title':{'$regex':'^[^解]*$'}})):
    print(i, document['title'])
    coll_to.save(document)
