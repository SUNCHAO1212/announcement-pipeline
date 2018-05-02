# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import tushare as ts
import codecs
from datetime import datetime

data = ts.get_stock_basics()

d = data.reset_index()

d = d[['code', 'name']]

today = datetime.now().strftime('%Y%m%d')
with codecs.open(today + '_stocks.txt', 'wb', 'utf8') as f:
    for dd in d.values:
        f.write('{}\t{}\n'.format(dd[0], dd[1]))
