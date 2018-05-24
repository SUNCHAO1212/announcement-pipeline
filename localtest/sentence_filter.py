# -*- coding:UTF-8 -*-
#!/usr/bin/env python3



import ahocorasick
import codecs
import re

from pymongo import MongoClient
from bs4 import BeautifulSoup


space = re.compile('\n')


def clean_sent(sent):
    sent = re.sub(space, '', sent.strip())
    return sent


# AC自动机，筛选没有词在词库中的句子
A = ahocorasick.Automaton()
with codecs.open('files/sentence_filter.txt', 'rb', 'utf8') as f:
    for ind, l in enumerate(f.readlines()):
        l = l.strip()
        A.add_word(l, (ind, l, len(l)))
A.make_automaton()


def input_filter(sent):
    for _ in A.iter(sent):
        return True
    return False


tables = re.compile('<lz.+?</lz>')


def sent_filter(html):
    # sents = content.split('。')
    # 丑陋的分段方式
    temp = re.sub(tables, '', html)
    sents = []
    temp = temp.split('一、')[-1]
    sents.append(temp.split('二、')[0])
    temp = temp.split('二、')[-1]
    sents.append(temp.split('三、')[0])
    temp = temp.split('三、')[-1]
    sents.append(temp.split('四、')[0])

    res = []
    for i, sent in enumerate(sents):
        if input_filter(sent):
            res.append(clean_sent(sent))
        else:
            pass

    return res


# def html_section(html, class_='Section'):
#     """ BeautifulSoup 方法 """
#     bs = BeautifulSoup(html, 'lxml')
#     sections = bs.find_all(class_=class_)
#     # second_sections = bs.find_all(class_='Second-Section')
#
#     split_tag = []
#     for i, section in enumerate(sections):
#         print(section)
#         split_tag.append(section)
#     sents = []
#     for i, tag in enumerate(split_tag):
#         if i == 0:
#             former, html = html.split(tag)
#         else:
#             former, html = html.split(tag)
#             sents.append(former)
#     else:
#         sents.append(html)
#     if class_ == 'Section':
#         res = []
#         for sent in sents:
#             res.append(html_section(sent, class_='Second-Section'))
#         return res
#     elif class_ == 'Second-Section':
#         if sents:
#             return sents
#         else:
#             return [html]


def html_section_v2(html, class_='"Section"'):
    # TODO 兼容多级目录，自动识别结构
    pt = re.compile('(<div class={}>.*?</div>)'.format(class_))
    split_tag = pt.findall(html)
    sents = []
    sents_dict = {}
    last_tag = ''
    for i, tag in enumerate(split_tag):
        if i == 0:
            former, html = html.split(tag)
        else:
            former, html = html.split(tag)
            sents.append(last_tag+former)
            # change data structure
            sents_dict[last_tag] = former
        last_tag = tag
    else:
        sents_dict[last_tag] = html
        sents.append(last_tag+html)

    if class_ == '"Section"':
        # res = []
        # for sent in sents:
        #     res.append(html_section_v2(sent, class_='"Second-Section"'))
        # return res

        # change data structure
        res_dict = {}
        for k in sents_dict:
            res_dict[k] = html_section_v2(sents_dict[k], class_='"Second-Section"')
        return res_dict
    elif class_ == '"Second-Section"':
        # if sents:
        #     return sents
        # else:
        #     return [html]

        if sents_dict:
            return sents_dict
        else:
            return html

if __name__ == '__main__':
    # client = MongoClient('192.168.1.251')
    # db = client.SecurityAnnouncement
    # coll = db.test2
    # jianchi_pattern = re.compile('^.*减持.*计划[的]公告$')
    # # for index, document in enumerate(coll.find({'crawOpt.secCode':'603117', 'title':{'$regex':'^.*减持.*计划公告$'}})):
    # for index, document in enumerate(coll.find({'url':'http://www.cninfo.com.cn/finalpage/2017-03-24/1203189193.PDF'})):
    #
    #     # sentences = sent_filter(document['crawOpt']['rawTxt'])
    #     sentences = sent_filter(document['rawHtml'])
    #     for j, s in enumerate(sentences):
    #         print(j, s)
    #     input()

    with open('referances/减持计划样例3（多事件）.html') as f:
        html = f.read()
        result = html_section_v2(html)
        for key, value in result.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    print(k,v)
            else:
                print(key, value)