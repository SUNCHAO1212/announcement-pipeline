# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import absolute_import, unicode_literals, print_function

import sys
from pymongo import MongoClient
import re

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

HOST = '192.168.1.251'
PORT = 27017

conn = MongoClient(host=HOST, port=PORT)
db = conn.NingBoData2

def zhaohui_rule():
    # pattern
    zhaohui_pats = [re.compile('(?P<e2>.*?)被(?P<e1>.*?)(?P<r>召回)'), re.compile('(?P<e1>.*?)对(?P<e2>.*?)(?P<r>发出消费者警告)'), re.compile('(?P<e1>.*?)对(?P<e2>.*?)实施.*?(?P<r>召回)'), re.compile('(?P<e1>.*?)(?P<r>召回)(?P<e2>.*)')]

    all_condition = db.webNews.find({'column': '扣留召回'}, {'title':1, '_id':0})
    for ind, all in enumerate(all_condition):
        extract_error = True
        for id, zhaohui_pat in enumerate(zhaohui_pats):
            matched = zhaohui_pat.match(all['title'])
            if matched:
                e1 = matched.group('e1')
                r = matched.group('r')
                e2 = matched.group('e2')
                if e2.startswith('部分') or e2.startswith('一款'):
                    e2 = e2[2:]

                if e1 and e2 and r:
                    print('{}:{}->{}->{}'.format(all['title'], e1, r, e2))
                    extract_error = False
                    break

        if extract_error:
            print('error:{}'.format(all['title']))



zhaohui_rule()

