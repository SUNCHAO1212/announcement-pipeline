# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import os
import re

from pymongo import MongoClient
from bs4 import BeautifulSoup


def mongo_data():
    client = MongoClient('192.168.1.251')
    db = client.SecurityAnnouncement
    coll = db.underweight_plan
    for document in coll.find():
        html = document['rawHtml']
        tables = pdf_table(html)
        if tables:
            print(tables)
        else:
            print('no table')
        # input()


table_classifier = {
    '主体信息': [],
    '减持计划': [],
    '增持计划': [],
}


ROOT = os.getcwd()
TABLE_PATH = 'files/table_classifier'
for key in table_classifier:
    with open(os.path.join(ROOT, TABLE_PATH, key)) as f:
        for line in f:
            table_classifier[key].append(line.strip())


def pdf_table(html, labels={'level1': '减持', 'level2': '计划'}):
    """
    :param html: 含有表格的html，表格形式：<lz data-tab="table-i-j">
    :param labels: 类别信息
    :return:
    """
    bs = BeautifulSoup(html, 'lxml')
    # print(bs.prettify())
    tables = bs.find_all('lz')
    # tables = bs.find_all(class_=re.compile('table.*'))
    result = {}
    for table in tables:
        # print(table.text)
        # print(table.prettify())
        label = labels['level1'] + labels['level2']
        for item2 in table_classifier[label]:
            if item2 in table.text:
                str2 = 'data-tab="' + table.attrs['data-tab'] + '"'
                result[label] = str2
                break
        else:
            for item1 in table_classifier['主体信息']:
                if item1 in table.text:
                    str1 = 'data-tab="' + table.attrs['data-tab'] + '"'
                    result['主体信息'] = str1
                    break
    return result


def kaggle_pdf(html):
    bs = BeautifulSoup(html, 'lxml')
    # print(bs.prettify())
    tables = bs.find_all('table')
    # tables = bs.find_all(class_=re.compile('table.*'))
    result = {}
    # print(tables)

    for table in tables:
        # print(table.text)
        # print(table.prettify())
        trs = table.find_all('tr')
        for i_tr, tr in enumerate(trs):
            tds = tr.find_all('td')
            for i_td, td in enumerate(tds):
                print(td.text)

    return result


if __name__ == '__main__':
    # mongo_data()

    # with open('referances/减持计划样例3（多事件）.html') as f:
    #     html = f.read()
    #     outer_tables = pdf_table(html)
    #     if outer_tables:
    #         print(outer_tables)
    #     else:
    #         print('no table')

    with open('referances/1205008030222222.html') as f:
        html = f.read()
        outer_tables = kaggle_pdf(html)
        # if outer_tables:
        #     print(outer_tables)
        # else:
        #     print('no table')