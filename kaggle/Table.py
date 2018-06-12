# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import re
import copy
import os
import json

from bs4 import BeautifulSoup

SCHEMA_PATH = '/home/sunchao/code/project/local-test/localtest/files/schema'
SCHEMA_FILE = 'schema/schema.json'

# 表格内文本清洗
space = re.compile('\s')


def clean_sent(sent):
    sent = space.sub('', sent.strip())
    return sent


class Table:
    html = ''
    event_type = ''
    len_row = 0
    len_col = 0
    info_number = 0
    array = []
    dic = {}
    schema = {}
    events = []
    add_info = {}

    def __init__(self, html_table, event_type):
        self.html = html_table
        self.event_type = event_type
        self.len_row, self.len_col = self.table_size()
        self.array = self.save_array()
        self.dic = self.get_dic()
        with open(SCHEMA_FILE) as f:
            self.schema = json.loads(f.read())[self.event_type]
        self.events = self.events()

    def table_size(self):
        trs = self.html.find_all('tr')
        len_row = len(trs)
        tr = trs[0]
        tds = tr.find_all('td')
        len_col = len(tds)
        for i_td, td in enumerate(tds):
            if td.attrs and 'colspan' in td.attrs:
                len_col += int(td.attrs['colspan']) - 1
        return len_row, len_col

    def save_array(self):
        array = []
        for i in range(self.len_row):
            array.append(copy.deepcopy([None]*self.len_col))
        trs = self.html.find_all('tr')

        for i_tr, tr in enumerate(trs):
            tds = tr.find_all('td')
            for i_td, td in enumerate(tds):
                if td.attrs:
                    if 'rowspan' in td.attrs:
                        for i in range(int(td.attrs['rowspan'])):
                            for j in range(i_td, self.len_col):
                                if array[i_tr + i][j] is None:
                                    array[i_tr + i][j] = clean_sent(td.text)
                                    break
                                else:
                                    pass
                    elif 'colspan' in td.attrs:
                        for i in range(int(td.attrs['colspan'])):
                            for j in range(i_td + i, self.len_col):
                                if array[i_tr][j] is None:
                                    array[i_tr][j] = clean_sent(td.text)
                                    break
                                else:
                                    pass
                    else:
                        for j in range(i_td, self.len_col):
                            if array[i_tr][j] is None:
                                array[i_tr][j] = clean_sent(td.text)
                                break
                            else:
                                pass
                else:
                    for j in range(i_td, self.len_col):
                        if array[i_tr][j] is None:
                            array[i_tr][j] = clean_sent(td.text)
                            break
                        else:
                            pass
        # 去除多余的行
        if array[-1][0] == '合计' or array[-1][1] == '合计':
            del array[-1]

        for i_row, row in enumerate(array):
            if row.count('/') > 1 or row.count('-') > 1 or row.count('') > 1:
                del array[i_row:]
                self.len_row = len(array)
                break
        return array

    def show_array(self):
        for row in self.array:
            for col in row:
                if col:
                    print(col, end='\t')
                else:
                    print('[void]', end='\t')
            print('')

    def show_table(self):
        trs = self.html.tbody.find_all('tr')
        for i_tr, tr in enumerate(trs):
            print("<tr[{}]>".format(i_tr))
            tds = tr.find_all('td')
            for i_td, td in enumerate(tds):
                print("<td[{}]>{}\t".format(i_td, re.sub('\s', '', td.text.strip())), end='\t')
            print('')

    def get_dic(self):
        keys = copy.deepcopy(self.array[0])
        value_start = 0
        for index in range(self.len_row):
            keys_set = set(keys)
            if len(keys_set) == self.len_col:
                value_start = index + 1
                break
                # return keys
            else:
                for i in range(self.len_col):
                    if keys[i] != self.array[index+1][i]:
                        keys[i] += '_'+self.array[index+1][i]
        temp_dict = {}
        for i, key in enumerate(keys):
            temp_dict[key] = []
            for row in range(value_start, self.len_row):
                temp_dict[key].append(self.array[row][i])
        self.info_number = self.len_row - value_start
        return temp_dict

    def new_entities(self, schema):
        entities = []
        # for sub_schema in schema:
        #     for role in schema[sub_schema]:
        #         entity = {
        #             "role": role,
        #             "type": sub_schema,
        #             "name": '',
        #             "externalReferences": [
        #                 {
        #                     "resource": "",
        #                     "reference": ""
        #                 }
        #             ]
        #         }
        #         entities.append(entity)

        for role in schema:
            entity = {
                "role": role,
                "type": self.event_type,
                "name": '',
                "externalReferences": [
                    {
                        "resource": "",
                        "reference": ""
                    }
                ]
            }
            entities.append(entity)
        return entities

    def new_event(self, event_type):

        entities = self.new_entities(self.schema)
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

    def events(self):
        events = []

        for i in range(self.info_number):
            event = self.new_event(self.event_type)
            for key, value in self.dic.items():
                trans_key = self.trans(key)
                if trans_key:
                    for entity in event['entities']:
                        if trans_key == entity['role']:
                            entity['name'] = self.dic[key][i]
                            break
                        else:
                            pass
                else:
                    print('Key error: ', key)
            events.append(event)

        return events

    def trans(self, key):
        # TODO 外部维护文件，对应若干表述的key
        return key


def table_events(html):
    bs = BeautifulSoup(html, 'lxml')
    tables = bs.find_all('table')
    for table in tables:

        table_example = Table(table, '股东增减持')

        return table_example.events


def main():
    with open('data/股东增减持/html/6927.html') as f:
        html = f.read()
        table_events(html)


if __name__ == '__main__':
    main()
