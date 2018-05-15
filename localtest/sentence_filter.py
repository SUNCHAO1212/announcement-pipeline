# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


from pymongo import MongoClient
import ahocorasick
import codecs
import re
import os


space = re.compile('\n')


def clean_sent(sent):
    sent = re.sub(space, '', sent.strip())
    return sent


# PATH = os.getcwd()
# print(PATH)

# AC自动机，筛选没有词在词库中的句子
A = ahocorasick.Automaton()
with codecs.open('files/trigger_words.txt', 'rb', 'utf8') as f:
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


if __name__ == '__main__':
    client = MongoClient('192.168.1.251')
    db = client.SecurityAnnouncement
    coll = db.test2
    jianchi_pattern = re.compile('^.*减持.*计划[的]公告$')
    # for index, document in enumerate(coll.find({'crawOpt.secCode':'603117', 'title':{'$regex':'^.*减持.*计划公告$'}})):
    for index, document in enumerate(coll.find({'url':'http://www.cninfo.com.cn/finalpage/2017-03-24/1203189193.PDF'})):

        # sentences = sent_filter(document['crawOpt']['rawTxt'])
        sentences = sent_filter(document['rawHtml'])
        for j, s in enumerate(sentences):
            print(j, s)
        input()