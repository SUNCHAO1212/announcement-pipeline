# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals, print_function

from pymongo import MongoClient
import os
import json
from functions.extr import Event_Extr
from functions.MQ import sent2mq


client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll = db.test


def reformat(input_dict):
    output_dict = {}
    for k in input_dict:
        output_dict[k] = input_dict[k][0]
    return output_dict


def merge_info(raw_info, event_info):
    all_info = event_info
    all_info['html'] = {
        "value": [
            [
                raw_info['html']
            ]
        ],
        "idTypeCn": "html",
        "idRoleCn": "召回原因",
        "required": "true"
    }
    all_info['公告名称'] = {
        "value": [
            [
                raw_info['title']
            ]
        ],
        "idTypeCn": "公告名称",
        "idRoleCn": "公告信息",
        "required": "true"
    }
    return all_info


def pipeline(docu):
    event_info = Event_Extr(docu['title'], docu['content'], docu['url'],
                            docu['eventType']['level1'], docu['eventType']['level2'])
    event_info = reformat(json.loads(event_info))
    result = merge_info(docu, event_info)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    for document in coll.find():
        print(pipeline(document))
