# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals, print_function

from pymongo import MongoClient
import os
import json
from localtest.extr import Event_Extr
from localtest.classifier import title2label
from localtest.PDFtables import pdf_table

ROOT = os.getcwd()
client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement



def supermind_format(docu, event_info, labels):
    # 表格分类
    tables = pdf_table(docu['rawHtml'])
    entities = reformat(event_info, tables)

    raw = docu['crawOpt']['rawTxt']
    html = docu['rawHtml']
    title = docu['title']
    url = docu['url']
    rawId = docu['rawId']
    formatTime = docu['publishTime']
    crawOpt = docu['crawOpt']

    # TODO 重命名 eventType
    eventType = '股东' + labels['level1'] + labels['level2'] + '事件'
    eventName = '股东' + labels['level1'] + labels['level2'] + '事件'

    # TODO 直接获得
    if event_info['证券简称'][0]['value'][0]:
        stockname = event_info['证券简称'][0]['value'][0][0]
    else:
        stockname = ''
    if event_info['证券代码'][0]['value'][0]:
        stockcode = event_info['证券代码'][0]['value'][0][0]
    else:
        stockcode = ''

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
                "entities": entities,
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
        "crawOpt": crawOpt
    }
    return all_info


def entity_format(entity_role, entity_type, entity_name, externalReferances):
    if entity_name:
        name = entity_name[0]
    else:
        name = ''
    entity = {
        "role": entity_role,
        "type": entity_type,
        "name": name,
        "externalReferences": externalReferances
    }
    return entity


def reformat(input_dict, tables):
    output_list = []
    for k in input_dict:
        value_list = input_dict[k][0]['value'][0]
        id_type = input_dict[k][0]['idTypeCn']
        role = input_dict[k][0]['idRoleCn']
        if id_type in tables:
            externalReferences = [
                {
                    "resource": "local_file",
                    "reference": tables[id_type]
                }
            ]
        else:
            externalReferences = [
                {
                    "resource": "",
                    "reference": ""
                }
            ]
        output_list.append(entity_format(role, id_type, value_list, externalReferences))

    return output_list


def pipeline(docu):
    # 两层json ?
    docu = json.loads(docu)
    docu = json.loads(docu)
    # 公告分类
    labels = title2label(docu['title'])
    if labels['level1'] == '其他' or labels['level2'] == '其他':
        return False

    # TODO 取消'extraInfo'改为'crawOpt'
    event_info = Event_Extr(docu['title'], docu['crawOpt']['rawTxt'], docu['url'],
                            labels['level1'], labels['level2'])
    result = supermind_format(docu, json.loads(event_info), labels)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    # coll = db.underweight_plan
    coll = db.test
    i = 1
    for document in coll.find():
        # print(document['_id'], type(document['_id']))
        document['rawId'] = str(document['_id'])
        del document['_id']

        res = json.loads(pipeline(json.dumps(json.dumps(document))))
        print(i, res)
        i += 1
        input()
