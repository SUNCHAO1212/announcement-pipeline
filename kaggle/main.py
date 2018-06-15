# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import os

from kaggle.ShareholdingChange import ShareholdingChange

if __name__ == '__main__':
    ROOT = '/home/sunchao/code/kaggle/round1_train_20180518/股东增减持'
    for root, _, filenames in os.walk(os.path.join(ROOT, 'pdf')):
        for i, filename in enumerate(filenames):
            filename = filename.split('.pdf')[0]
            print('处理第{}篇文档：{}'.format(i, filename))

            filename = '6927'

            SC = ShareholdingChange(filename)
            print(SC.all_info)

            input()
