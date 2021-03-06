# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from __future__ import absolute_import, unicode_literals, print_function


import os
import json
import copy
import time
import hashlib
from pymongo import MongoClient

from localtest.extr import Event_Extr
from localtest.classifier import title2label
from localtest.PDFtables import pdf_table
from localtest.sentence_filter import sent_filter
from localtest.Table import table_events

ROOT = os.getcwd()
SCHEMA_PATH = 'files/schema'
PIPELINE_NAME = 'local_guquanbiandong'


def supermind_format(docu, events, event_type):
    # 表格分类信息
    tables = pdf_table(docu['rawHtml'])
    events = add_table_info(events, tables)
    # 文档信息
    raw = docu['rawHtml']
    html = docu['rawHtml']
    title = docu['title']
    url = docu['url']
    raw_id = docu['rawId']
    craw_opt = docu['crawOpt']
    # uuid: pipeline名 + url MD5
    string = PIPELINE_NAME + docu['url']
    hl = hashlib.md5()
    hl.update(string.encode(encoding='utf-8'))
    uuid = hl.hexdigest()
    # 事件信息
    mention_time = docu['publishTime']
    format_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(mention_time, '%Y-%m-%d'))
    # format_time = ''
    stock_code = docu['crawOpt']['secCode']
    stock_name = docu['crawOpt']['secName']
    # stock_code = ''
    # stock_name = ''
    event_name = stock_name + '_' + event_type + '_' + time.strftime('%Y%m%d', time.strptime(mention_time, '%Y-%m-%d'))
    # event_name = event_type + docu['title']
    for event in events:
        event['eventName'] = event_name
        event['externalInfo']['stockname'] = stock_name
        event['externalInfo']['stockcode'] = stock_code
        event['eventTime']['mention'] = mention_time
        event['eventTime']['formatTime'] = format_time

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
            "rawId": raw_id,
            "uuid": uuid,
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
        "crawOpt": craw_opt
    }
    return all_info


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
    event = {
            "eventId": "1234567890",
            "eventName": "",
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
                        # TODO 合并策略：现在只取第一条，需要多条对应。不要改格式
                        e['name'] = entity['value'][0][0]
                        # e['name'] = entity['value'][0]
                    break
    if rest_entities[0]:
        # TODO 通过某种策略舍弃多余的事件
        if len(rest_entities[0]) < 4:
            return events
        return events + event_integrate(rest_entities, event_type)
    else:
        return events


def multi_event_extr(sent_lists, docu, event_type):
    """
    :param sent_lists:
    :param docu:
    :param event_type:
    :return: all events without table information
    """
    # event_type = '股东' + labels['level1'] + labels['level2'] + '事件'
    # 按顺序保留句子信息
    all_entities = []
    for i, sent in enumerate(sent_lists):
        temp_list = []
        infos = Event_Extr(docu['title'], sent, docu['url'], event_type, '.*')
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
    event_type = title2label(docu['title'])

    if event_type != '股东股权质押事件':
        # 分句信息抽取
        sentences = sent_filter(docu['rawHtml'])
        event_info = multi_event_extr(sentences, docu, event_type)
    else:
        # 表格信息抽取
        event_info = table_events(docu['rawHtml'])


    # 重组格式
    result = supermind_format(docu, event_info, event_type)
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':

    client = MongoClient('192.168.1.251')
    db = client.SecurityAnnouncement
    # coll = db.pledge
    coll = db.pledge_filtered

    temp_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/szse/bulletin_detail/true/1204625933'
    # for index, document in enumerate(coll.find({'crawOpt.secName':'通鼎互联', 'title':{'$regex':'^[^解]*$'}})):
    # for document in coll.find({'url':temp_url}):
    for document in coll.find():

        print(document['title'], document['url'])
        document['rawId'] = str(document['_id'])
        del document['_id']
        # # temp
        # try:
        #     temp = json.dumps(document)
        #     temp = json.dumps(temp)
        #     temp = pipeline(temp)
        #     if temp:
        #         res = json.loads(temp)
        #         for outer_event in res['events']:
        #             for outer_entity in outer_event['entities']:
        #                 print(outer_entity['role'], outer_entity['name'])
        #             print('\n')
        #         print(res)
        #     else:
        #         pass
        # except Exception as e:
        #     print(e)

        temp = json.dumps(document)
        temp = json.dumps(temp)
        temp = pipeline(temp)
        if temp:
            res = json.loads(temp)
            for outer_event in res['events']:
                for outer_entity in outer_event['entities']:
                    print(outer_entity['role'], outer_entity['name'])
                print('\n')
            print(res)
        else:
            print('no output from pipeline')
            pass

        # res = json.loads(pipeline(json.dumps(json.dumps(document))))

        # input()
