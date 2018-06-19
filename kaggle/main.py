# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import os
import re
import calendar
import time

from kaggle.ShareholdingChange import ShareholdingChange


def main():
    ROOT = '/home/sunchao/code/kaggle/round1_train_20180518/股东增减持'
    for root, _, filenames in os.walk(os.path.join(ROOT, 'pdf')):
        for i, filename in enumerate(filenames):
            filename = filename.split('.pdf')[0]
            print('处理第{}篇文档：{}'.format(i, filename))

            # filename = '1124313'

            SC = ShareholdingChange(filename)

            if SC.all_info['record']:
                print(SC.all_info)
            else:
                print('No info')


def test():
    key = '本次减持计划完成前持有股份_占总股数比例'
    before_num_pt = re.compile('.*[增减]持.*前.*持有的?股份.*(?:股数|持有股份)[^比]*$')
    res = before_num_pt.search(key)
    print(res.group())


if __name__ == '__main__':
    main()
    # test()