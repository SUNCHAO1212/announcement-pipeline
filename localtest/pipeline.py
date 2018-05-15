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


def supermind_format(docu, events, labels):
    # 表格分类信息
    tables = pdf_table(docu['rawHtml'])
    events = add_table_info(events, tables)
    # 文档信息
    raw = docu['crawOpt']['rawTxt']
    html = docu['rawHtml']
    title = docu['title']
    url = docu['url']
    rawId = docu['rawId']
    crawOpt = docu['crawOpt']
    # 事件信息
    event_type = '股东' + labels['level1'] + labels['level2'] + '事件'
    format_time = docu['publishTime']
    stock_code = docu['crawOpt']['secCode']
    stock_name = docu['crawOpt']['secName']
    for event in events:
        event['externalInfo']['stockname'] = stock_code
        event['externalInfo']['stockcode'] = stock_name
        event['eventTime']['formatTime'] = format_time
        for entity in event['entities']:
            entity['type'] = event_type
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


# def entity_format(entity_role, entity_type, entity_name, externalReferences):
#     if entity_name:
#         name = entity_name[0]
#     else:
#         name = ''
#     entity = {
#         "role": entity_role,
#         "type": entity_type,
#         "name": name,
#         "externalReferences": externalReferences
#     }
#     return entity


def add_table_info(events, tables):
    """ 为事件添加表格信息 """
    if tables:
        for event in events:
            entities = event['entities']
            for entity in entities:
                id_type = entity['type']
                if id_type in tables:
                    entity['externalReferences'][0]['resource'] = "local_file"
                    entity['externalReferences'][0]['reference'] = tables[id_type]

    return events


def new_entities(schema):
    entities = []
    for sub_schema in schema:
        for role in schema[sub_schema]:
            entity = {
                "role": role,
                "type": sub_schema,
                "name": '',
                "externalReferences" :[
                    {
                        "resource": "",
                        "reference": ""
                    }
                ]
            }
            entities.append(entity)
    return entities


def new_event(event_type):
    with open(os.path.join(ROOT, SCHEMA_PATH, event_type)) as f:
        schema = json.loads(f.read())
    entities = new_entities(schema)
    # TODO 事件字段填充
    event = {
            "eventId": "1234567890",
            "eventName": event_type,
            "location": {
                "name": "",
                "references": []
            },
            "externalInfo": {
                "stockname": '',
                "stockcode": ''
            },
            "eventTime": {
                "mention": "",
                "formatTime": ''
            },
            "eventType": event_type,
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


def event_integrate(entities, event_type):
    """
    :param entities:
    :param event_type:
    :return: integrated events
    """
    events = []
    events.append(copy.deepcopy(new_event(event_type)))
    rest_entities = [[]]
    for ind, entities_list in enumerate(entities):
        for i, entity in enumerate(entities_list):
            for e in events[0]['entities']:
                if entity['idRoleCn'] == e['role']:
                    if e['name']:
                        rest_entities[0].append(entity)
                    else:
                        e['name'] = entity['value'][0][0]
                    break
    if rest_entities[0]:
        return events + event_integrate(rest_entities, event_type)
    else:
        return events


def multi_event_extr(sent_lists, docu, labels):
    """
    :param sent_lists:
    :param docu:
    :param labels:
    :return: all events without table information
    """
    # TODO 合并完整事件
    event_type = '股东' + labels['level1'] + labels['level2'] + '事件'
    # stockname = 'test'
    # stockcode = 'test'
    # formatTime = 'test'
    # events = []
    # mainbody = copy.deepcopy(event)
    # events.append(copy.deepcopy(new_event(event_type)))

    # 按顺序保留句子信息
    all_entities = []
    for i, sent in enumerate(sent_lists):
        temp_list = []
        infos = Event_Extr(docu['title'], sent, docu['url'], labels['level1'], labels['level2'])
        infos = json.loads(infos)
        # TODO 无模版容错
        for k in infos:
            if infos[k][0]['value'][0]:
                temp_list.append(infos[k][0])
            else:
                pass
        if temp_list:
            all_entities.append(temp_list)
        # print(temp_list)
    # TODO 合并
    events = event_integrate(all_entities, event_type)

    return events


def pipeline(docu):
    """
    :param docu:
    :return: supermind 约定接口，pipeline 输出格式
    """
    # 两层json ?
    docu = json.loads(docu)
    docu = json.loads(docu)
    # 公告分类
    labels = title2label(docu['title'])
    if labels['level1'] == '其他' or labels['level2'] == '其他':
        return False

    # 分句信息抽取 todo
    # sentences = sent_filter(docu['crawOpt']['rawTxt'])
    sentences = sent_filter(docu['rawHtml'])
    # sentences = sent_filter(docu['rawHtml'])
    event_info = multi_event_extr(sentences, docu, labels)

    # 重组格式
    result = supermind_format(docu, event_info, labels)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    import re
    jianchi_pattern = re.compile('^.*减持.*计划[的]公告$')
    client = MongoClient('192.168.1.251')
    db = client.SecurityAnnouncement
    coll = db.underweight_plan
    # coll = db.test2
    cnt = 0
    # ^.*减持.*计划[的]公告$
    for document in coll.find():
        cnt += 1
        if not jianchi_pattern.match(document['title']):
            continue
        print(document['title'], document['url'])

        print(cnt)
        # print(document['_id'], type(document['_id']))
        document['rawId'] = str(document['_id'])
        del document['_id']
        # # temp
        temp = json.dumps(document)
        temp = json.dumps(temp)
        # temp = json.dumps(temp)
        temp = pipeline(temp)
        if temp:
            res = json.loads(temp)
            for event in res['events']:
                for entity in event['entities']:
                    print(entity['role'], entity['name'])
                print('\n')
            print(res)
        else:
            pass

        # res = json.loads(pipeline(json.dumps(json.dumps(document))))

        # input()
