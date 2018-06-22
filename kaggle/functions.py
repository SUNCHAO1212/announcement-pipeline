# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import copy
import os

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

LTP_DATA_DIR = '/home/sunchao/code/python_env_models/ltp_data_v3.4.0'
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')


def segmentor(sentence):
    segmentor = Segmentor()  # 初始化实例
    # segmentor.load(cws_model_path)  # 加载模型
    segmentor.load_with_lexicon(cws_model_path, '/home/sunchao/code/python_env_models/ltp_data_v3.4.0/lexicon.txt')
    words = segmentor.segment(sentence)  # 分词
    words_list = list(words)
    print(words_list)
    segmentor.release()  # 释放模型
    return words_list


def postager(words_list):
    postager = Postagger()
    postager.load(pos_model_path)
    postags = postager.postag(words_list)
    postags_list = list(postags)
    print(postags_list)
    postager.release()
    return postags_list


def ner(words, postags):
    recognizer = NamedEntityRecognizer()  # 初始化实例
    recognizer.load(ner_model_path)  # 加载模型

    nertags = recognizer.recognize(words, postags)  # 命名实体识别
    nertags_list = list(nertags)
    print(nertags_list)
    recognizer.release()  # 释放模型
    return nertags


def parser(words, postags):
    parser = Parser()  # 初始化实例
    parser.load(par_model_path)  # 加载模型
    arcs = parser.parse(words, postags)
    print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    parser.release()


def main():
    sentence = '''2014年6月5日，沙河实业股份有限公司（以下简称“公司”）收到股东三亚成大投资有限公司(以下简称“三亚成大”)及其一致行动人海南德瑞实业有限公司（以下简称“海南德瑞”）的减持通知。三亚成大及海南德瑞于 2014 年 4 月 23 日至 2014 年 6 月 2 日期间，通过深圳证券交易所集中竞价交易系统减持公司无限售流通股股份5,927,580 股，占公司总股本的'''
    words_list = segmentor(sentence)
    postags_list = postager(words_list)
    nertags_list = ner(words_list, postags_list)
    parser(words_list, postags_list)
    for i, item in enumerate(words_list):
        print(words_list[i], postags_list[i], nertags_list[i])


if __name__ == '__main__':
    main()