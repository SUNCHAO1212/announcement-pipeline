# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from pymongo import MongoClient
import time
import os


HOST = '192.168.1.251'
PORT = '27017'


client = MongoClient(host=HOST)
db = client.SecurityAnnouncement
coll = db.test

HTMLPATH = '/home/sunchao/code/project/local-test/localtest/myResultHtml'
TXTPATH = '/home/sunchao/code/project/local-test/localtest/myResultTxt'


def upload(filename):
    title = filename.split('.')[0]
    with open(os.path.join(HTMLPATH, title, 'lz.html')) as f:
        html = f.read()
    with open(os.path.join(TXTPATH, title+'.txt')) as f:
        content = f.read()
    publishTime = '2018-4-27'
    creationTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    coll.save(
        dict(
            title=title,
            html=html,
            content=content,
            publishTime=publishTime,
            creationTime=creationTime,
            url='http://www.cninfo.com.cn/cninfo-new/disclosure/fulltext/bulletin_detail/true/.*',
            eventType={
                'level1': '减持',
                'level2': '计划'
            }
        )
    )


if __name__ == '__main__':
    # for root, _, filenames in os.walk('/home/sunchao/code/project/local-test/localtest/download'):
    #     for filename in filenames:
    #         upload(filename)

    print("setence".split())
