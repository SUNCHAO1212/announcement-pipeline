# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
import ahocorasick
import codecs

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


table1_list = ['持股数量', '持股比例', '股东身份', '股份来源']
table2_list = ['减持数量', '减持比例', '减持方式', '减持期间', '价格区间', '减持原因', '减持股份来源']


def pdf_table(html):

    bs = BeautifulSoup(html, 'lxml')
    # print(bs.prettify())
    tables = bs.find_all('lz')
    # res2 = bs.find_all(class_=re.compile('table.*'))
    result = {}
    for table in tables:
        # print(table.text)
        # print(table.prettify())
        for item2 in table2_list:
            if item2 in table.text:
                str2 = 'data-tab="' + table.attrs['class'][0] + '"'
                result['事件信息'] = str2
                break
        else:
            for item1 in table1_list:
                if item1 in table.text:
                    str1 = 'data-tab="' + table.attrs['class'][0] + '"'
                    result['主体信息'] = str1
                    break

    return result


def local_test():
    pass


if __name__ == '__main__':
    # mongo_data()

    with open('referances/减持计划样例1.html') as f:
        html = f.read()
        tables = pdf_table(html)
        if tables:
            print(tables)
        else:
            print('no table')
