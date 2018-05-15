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


# TODO 改成读文件方式
tables = {
    '主体信息': [],
    '减持计划': [],
    '增持计划': [],
}
# with open()
table1_list = ['持股数量', '持股比例', '股东身份', '股份来源']
table2_list = ['减持数量', '减持比例', '减持方式', '减持期间', '价格区间', '减持原因', '减持股份来源']
table3_list = ['']


def pdf_table(html, labels={}):
    """ 根据文档类别选择不同的表格筛选特征词 """
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
                str2 = 'data-tab="' + table.attrs['data-tab'] + '"'
                result['减持计划'] = str2
                break
        else:
            for item1 in table1_list:
                if item1 in table.text:
                    str1 = 'data-tab="' + table.attrs['data-tab'] + '"'
                    result['主体信息'] = str1
                    break
    return result


if __name__ == '__main__':
    # mongo_data()

    # with open('referances/减持计划样例1.html') as f:
    #     html = f.read()
    #     tables = pdf_table(html)
    #     if tables:
    #         print(tables)
    #     else:
    #         print('no table')
    list1 = []
    with open('files/table_classifier/主体信息') as f:
        for line in f:
            list1.append(line.strip())
    print(list1)