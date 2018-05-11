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


def sent_filter(content):
    sents = content.split('。')
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
    coll = db.underweight_plan
    for index, document in enumerate(coll.find()):
        res = sent_filter(document['extraInfo']['rawTxt'])
        for j, s in enumerate(res):
            print(j, s)
        input()