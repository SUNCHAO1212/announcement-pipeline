# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from __future__ import absolute_import, unicode_literals, print_function

import os
import json
from localtest.extr import Event_Extr
from localtest.classifier import title_label
from localtest.pdf2html import getPdf2html
from localtest.MQ import sent2mq

import sys
import os

ROOT = os.getcwd()
PDFDIR = 'download'
TXTDIR = 'myResultTxt'
HTMLDIR = 'myResultHtml'


def reformat(input_dict, filename):
    output_dict = {}
    for k in input_dict:
        try:
            # print(k, input_dict[k][0])
            if k == '发布日期':
                if input_dict[k][0]['value'][0] == []:
                    output_dict[k] = input_dict[k][0]
                else:
                    temp = input_dict[k][0]
                    temp['value'][0] = [temp['value'][0][-1]]
                    output_dict[k] = temp
                # print(output_dict[k])
            else:
                output_dict[k] = input_dict[k][0]
        except:
            pass
    title = {
        "value": [
            [
                filename
            ]
        ],
        "idTypeCn": "公告名称",
        "idRoleCn": "公告信息",
        "required": "true"
    }
    output_dict['公告名称'] = title
    try:
        html = {
            "value": [
                [
                    "string"
                ]
            ],
            "idTypeCn": "HTML",
            "idRoleCn": "公告全文",
            "required": "true"
        }
        with open(os.path.join(ROOT, HTMLDIR, filename, 'lz.html')) as f:
            html['value'][0][0] = f.read()
        output_dict['html'] = html
    except Exception as e:
        print(e)
    return output_dict


URL = 'http://www.cninfo.com.cn/cninfo-new/disclosure/fulltext/bulletin_detail/true/.*'


def format_data(title):
    label = title_label(title)
    if label['level1'] != '其他' and label['level2'] != '其他':
        try:
            with open(os.path.join(ROOT, TXTDIR, title + '.txt')) as f:
                content = f.read()
                data_dict = {
                    'column': label['level1'],
                    'title': title,
                    'content': content,
                    'url': URL,
                    'topic': label['level2'],
                }
            return data_dict
        except Exception as e:
            print(e)


def old_pipeline():
    # 预处理，PDF转HTML
    # getPdf2html(os.path.join(ROOT, PDFDIR))
    # 信息抽取
    for root, dirs, filenames in os.walk(os.path.join(ROOT, PDFDIR)):
        for filename in filenames:
            filename = filename.split('.PDF')[0]
            # print(filename)
            try:
                temp = format_data(filename)
                result = Event_Extr(temp['title'], temp['content'], temp['url'], temp['column'], temp['topic'])
                result = json.loads(result)
                result = reformat(result, filename)

                # for k in result:
                #     print(k, result[k])
                print(result)
            except Exception as e:
                print(e)


if __name__ == "__main__":

    old_pipeline()
