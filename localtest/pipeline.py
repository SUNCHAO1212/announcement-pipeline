# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals, print_function

from pymongo import MongoClient
import os
import json
import copy

from localtest.extr import Event_Extr
from localtest.classifier import title2label
from localtest.PDFtables import pdf_table
from localtest.sentence_filter import sent_filter


ROOT = os.getcwd()
SCHEMA_PATH = 'files/schema'
client = MongoClient('192.168.1.251')
db = client.SecurityAnnouncement


def supermind_format(docu, events, labels):
    # 表格分类
    tables = pdf_table(docu['rawHtml'])
    events = reformat(events, tables, docu)
    raw = docu['crawOpt']['rawTxt']
    html = docu['rawHtml']
    title = docu['title']
    url = docu['url']
    rawId = docu['rawId']
    # formatTime = docu['publishTime']
    crawOpt = docu['crawOpt']


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
        "events": events,
        "crawOpt": crawOpt
    }
    return all_info


def entity_format(entity_role, entity_type, entity_name, externalReferences):
    if entity_name:
        name = entity_name[0]
    else:
        name = ''
    entity = {
        "role": entity_role,
        "type": entity_type,
        "name": name,
        "externalReferences": externalReferences
    }
    return entity


def event_format(eventName, eventType, docu, entities):
    event = {
            "eventId": "1234567890",
            "eventName": eventName,
            "location": {
                "name": "",
                "references": []
            },
            "externalInfo": {
                "stockname": docu['crawOpt']['secName'],
                "stockcode": docu['crawOpt']['secCode']
            },
            "eventTime": {
                "mention": "",
                "formatTime": docu['publishTime']
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
    return event


def reformat(events, tables, docu):
    new_events = []
    for event_type in tables:
        # todo
        temp_entities = []
        with open(os.path.join(ROOT, SCHEMA_PATH, event_type)) as f:
            for schema_role in f:
                temp_entities.append(entity_format(schema_role.strip(), event_type, ['见表格'], externalReferences=[{"resource": "local_file", "reference": tables[event_type]}]))
        temp_event = event_format(event_type, event_type, docu, temp_entities)
        new_events.append(copy.deepcopy(temp_event))

    for event in events:
        if event['entities']:
            entities = event['entities']
            temp_entities = []
            for entity in entities:
                value_list = entity['value'][0]
                id_type = entity['idTypeCn']
                role = entity['idRoleCn']
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
                temp_entities.append(entity_format(role, id_type, value_list, externalReferences))
            event['entities'] = copy.deepcopy(temp_entities)
            new_events.append(copy.deepcopy(event))
        else:
            pass

    # output_list = []
    # for k in input_dict:
    #     value_list = input_dict[k][0]['value'][0]
    #     id_type = input_dict[k][0]['idTypeCn']
    #     role = input_dict[k][0]['idRoleCn']
    #     if id_type in tables:
    #         externalReferences = [
    #             {
    #                 "resource": "local_file",
    #                 "reference": tables[id_type]
    #             }
    #         ]
    #     else:
    #         externalReferences = [
    #             {
    #                 "resource": "",
    #                 "reference": ""
    #             }
    #         ]
    #     output_list.append(entity_format(role, id_type, value_list, externalReferences))

    return new_events


def multi_event_extr(sent_lists, docu, labels):
    # TODO 合并完整事件
    # TODO 重命名 eventType
    eventType = '股东' + labels['level1'] + labels['level2'] + '事件'
    eventName = '股东' + labels['level1'] + labels['level2'] + '事件'
    stockname = 'test'
    stockcode = 'test'
    formatTime = 'test'
    events = []
    event = {
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
            "entities": [],
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
    mainbody = copy.deepcopy(event)
    events.append(copy.deepcopy(event))
    # TODO 对顺序出现的句子进行事件合并
    all_entities = []
    # 按顺序保留句子信息
    for i, sent in enumerate(sent_lists):
        temp_list = []
        infos = Event_Extr(docu['title'], sent, docu['url'], labels['level1'], labels['level2'])
        infos = json.loads(infos)
        for k in infos:
            if infos[k][0]['value'][0]:
                temp_list.append(infos[k][0])
            else:
                pass
        if temp_list:
            all_entities.append(temp_list)
    # 合并
    last = 0
    temp_role = []
    mainbody_info = {
        'idTypeCn':[],
        'idRoleCn':[],
        'value':[]
    }
    for ind, entities_list in enumerate(all_entities):
        for i, entity in enumerate(entities_list):
            if entity['idTypeCn'] == '主体信息':
                if entity['idRoleCn'] in mainbody_info['idRoleCn'] and entity['value'] in mainbody_info['value']:
                    pass
                else:
                    mainbody['entities'].append(entity)
                    mainbody_info['idRoleCn'].append(entity['idRoleCn'])
                    mainbody_info['value'].append(entity['value'])
            elif entity['idTypeCn'] == '事件信息':
                if temp_role and (ind-last > 2 or entity['idRoleCn'] in temp_role):
                    # 合并并保存
                    events.append(copy.deepcopy(event))
                    temp_role = [entity['idRoleCn']]
                else:
                    temp_role.append(entity['idRoleCn'])
                events[-1]['entities'].append(entity)
                last = ind
            else:
                # print('公告信息', entity)
                pass
    events.append(mainbody)
    return events


def pipeline(docu):
    # 两层json ?
    docu = json.loads(docu)
    docu = json.loads(docu)
    # 公告分类
    labels = title2label(docu['title'])
    if labels['level1'] == '其他' or labels['level2'] == '其他':
        return False
    sentences = sent_filter(docu['crawOpt']['rawTxt'])
    event_info = multi_event_extr(sentences, docu, labels)

    # event_info = Event_Extr(docu['title'], docu['crawOpt']['rawTxt'], docu['url'],
    #                         labels['level1'], labels['level2'])

    result = supermind_format(docu, event_info, labels)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    coll = db.underweight_plan
    # coll = db.test2
    for document in coll.find():
        # print(document['_id'], type(document['_id']))
        document['rawId'] = str(document['_id'])
        del document['_id']

        # temp
        temp = json.dumps(document)
        temp = json.dumps(temp)
        # temp = json.dumps(temp)
        temp = pipeline(temp)
        if temp:
            res = json.loads(temp)
            print(res)
        else:
            pass

        # res = json.loads(pipeline(json.dumps(json.dumps(document))))

        # input()
