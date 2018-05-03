# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals, print_function

from pymongo import MongoClient
import os
import json
from localtest.extr import Event_Extr
from localtest.MQ import sent2mq
from localtest.classifier import title2label
from localtest.mysql import update_mysql


ROOT = os.getcwd()
client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement
coll = db.test


def supermind_format(docu, event_info, labels):

    raw = docu['extraInfo']['rawTxt']
    html = docu['rawHtml']
    title = docu['title']
    url = docu['url']
    rawId = str(docu['_id'])
    eventName = labels['level1'] + '_' + labels['level2']
    if event_info['证券简称'][0]['value'][0]:
        stockname = event_info['证券简称'][0]['value'][0][0]
    else:
        stockname = ''
    if event_info['证券代码'][0]['value'][0]:
        stockcode = event_info['证券代码'][0]['value'][0][0]
    else:
        stockcode = ''
    formatTime = docu['publishTime']
    eventType = labels['level1'] + '_' + labels['level2']
    all_info = {
        "nafVer": {
            "lang": "cn",
            "version": "v1.0"
        },
        "raw": raw,
        "cleaned_raw": '',
        "nafHeader": {
            "title": title,
            "rawHtml": html,
            "url": url,
            "rawId": rawId,
            "uuid": "",
            "docId": ""
        },
        "entities": [
            {
                "references": [
                    {
                        "charseq": {
                            "start": 0,
                            "end": 0
                        }
                    }
                ],
                "type": "",
                "id": "",
                "externalReferences": [
                    {
                        "resource": "",
                        "reference": ""
                    }
                ]
            }
        ],
        "events": [
            {
                "eventId": "1234567890",
                "eventName": eventName,
                "location": {
                    "name": "",
                    "references": []
                },
                "externalInfo": {
                    "stockname": stockname,
                    "stockcode": stockcode
                },
                "eventTime": {
                    "mention": "",
                    "formatTime": formatTime
                },
                "eventType": eventType,
                "eventPolarity": "",
                "eventTense": "Unspecified",
                "eventModality": "Asserted",
                "entities": reformat(event_info),
                "predicate": {
                    "mention": "",
                    "externalReferences": [
                        {
                            "resource": "",
                            "reference": ""
                        }
                    ]
                }
            }
        ],
        "crawOpt": {
        }
    }
    return all_info


def entity_format(entity_role, entity_type, entity_name):
    if entity_name:
        name = entity_name[0]
    else:
        name = ''
    entity = {
        "role": entity_role,
        "type": entity_type,
        "name": name,
        "externalReferences": [
            {
                "resource": "",
                "reference": ""
            }
        ]
    }
    return entity


def reformat(input_dict):
    output_list = []
    for k in input_dict:
        value_list = input_dict[k][0]['value'][0]
        id_type = input_dict[k][0]['idTypeCn']
        role = input_dict[k][0]['idRoleCn']
        # print(k, value_list, id_type, role)
        output_list.append(entity_format(role, id_type, value_list))

    return output_list


def pipeline(docu):
    # 更新sql时间
    # update_mysql()
    labels = title2label(docu['title'])
    if labels['level1'] == '其他' or labels['level2'] == '其他':
        return False
    event_info = Event_Extr(docu['title'], docu['extraInfo']['rawTxt'], docu['url'],
                            labels['level1'], labels['level2'])
    result = supermind_format(docu, json.loads(event_info), labels)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    for document in coll.find():
        res = json.loads(pipeline(document))
        print(res['events'][0]['entities'][6])
        input()
