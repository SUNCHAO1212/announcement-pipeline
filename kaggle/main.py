# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import os
import re
import calendar
import time

from kaggle.ShareholdingChange import ShareholdingChange


def main():

    ROOT = '/home/sunchao/code/kaggle/FDDC_announcements_round1_test_a_20180605/股东增减持'
    for root, _, filenames in os.walk(os.path.join(ROOT, 'pdf')):
        records = []
        row_1 = '公告id	股东全称	股东简称	变动截止日期	变动价格	变动数量	变动后持股数	变动后持股比例'
        records.append(row_1)
        for i, filename in enumerate(filenames):
            try:
                filename = filename.split('.pdf')[0]
                print('处理第{}篇文档：{}'.format(i, filename))

                # filename = '1008005'

                SC = ShareholdingChange(filename)

                if SC.all_info['record']:
                    print(SC.all_info)
                    for item in SC.all_info['record']:
                        result = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(item['公告id'],item['股东全称'],item['股东简称'],
                                                                         item['变动截止日期'],item['变动价格'],item['变动数量'],
                                                                         item['变动后持股数'],item['变动后持股比例'],)
                        records.append(result)
                else:
                    print('No info')
            except Exception as e:
                print(e)
        with open('zengjianchi.txt', 'w') as fo:
            for item in records:
                fo.write(item + '\n')


def test():
    ROOT = '/home/sunchao/code/kaggle/FDDC_announcements_round1_test_a_20180605/股东增减持'
    for root, _, filenames in os.walk(os.path.join(ROOT, 'pdf')):
        records = []
        row_1 = '公告id	股东全称	股东简称	变动截止日期	变动价格	变动数量	变动后持股数	变动后持股比例'
        records.append(row_1)
        for i, filename in enumerate(filenames):

            filename = filename.split('.pdf')[0]
            print('处理第{}篇文档：{}'.format(i, filename))

            # filename = '1629269'

            SC = ShareholdingChange(filename)

            if SC.all_info['record']:
                print(SC.all_info)
                for item in SC.all_info['record']:
                    result = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(item['公告id'],item['股东全称'],item['股东简称'],
                                                                     item['变动截止日期'],item['变动价格'],item['变动数量'],
                                                                     item['变动后持股数'],item['变动后持股比例'],)
                    records.append(result)
            else:
                print('No info')


def format_date(date='20161122'):

    pt1 = re.compile('.*(?:(?P<year>\d{4})年)?.*(?P<month>\d+)月(?:(?P<day>\d+)日)?')
    pt2 = re.compile('.*(?P<year>\d{4}).*[.-](?P<month>\d+)[.-](?P<day>\d+)')
    pt3 = re.compile('.*(?P<year>\d{4}).*[\/](?P<month>\d+)[\/](?P<day>\d+)')
    pt4 = re.compile('\d{8}')

    res1 = pt1.search(date)
    res2 = pt2.search(date)
    res3 = pt3.search(date)
    res4 = pt4.search(date)

    year, month, day = 0, 0, 0

    if res1:
        if res1.group('year'):
            day = int(res1.group('year'))
        month = int(res1.group('month'))
        if res1.group('day'):
            day = int(res1.group('day'))
    elif res2:
        if res2.group('year'):
            day = int(res2.group('year'))
        month = int(res2.group('month'))
        if res2.group('day'):
            day = int(res2.group('day'))
    elif res3:
        year = int(res3.group('year'))
        month = int(res3.group('month'))
        if res3.group('day'):
            day = int(res3.group('day'))
        else:
            day = 0
    elif res4:
        temp = res4.group()
        year = int(temp[0:4])
        month = int(temp[4:6])
        day = int(temp[6:8])
    else:
        print('[Error] 错误的日期')
    # 只有年月
    if day == 0:
        _, day = calendar.monthrange(year, month)

    date = '%4d-%02d-%02d' % (year, month, day)
    return date


def fc():
    def match(matched):
        temp = matched.group(0)
        print(matched.group(0), matched.group(1))
        temp = re.sub(matched.group(0), matched.group(1), temp)
        print(temp)
        return temp
    sent = 'asdf8976kjh'
    pt = re.compile('.*?(\d+).*')
    # res = re.sub('.*??(\d+).*', match, sent)
    res = pt.sub(match, sent)
    print(res)


if __name__ == '__main__':
    # format_date()

    # main()
    # test()

    fc()