# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import json
import re
import os
import copy

from bs4 import BeautifulSoup
from kaggle.extr import Event_Extr
from kaggle.Table import Table
from kaggle.LzPdf2Html.create_new_html import lz_pdf2html

SCHEMA_FILE = 'schema/schema.json'

# ROOT = '/home/sunchao/code/kaggle/round1_train_20180518'
ROOT = '/home/sunchao/code/kaggle/FDDC_announcements_round1_test_a_20180605'

# 文本清洗
space_pt = re.compile('\s+')


def clean_sent(sent):
    sent = space_pt.sub('', sent)
    return sent


class InformationExtraction(object):
    # 定义基本属性
    label = ''
    id = ''
    schema = {}
    html = ''
    html_for_table = ''
    text = ''
    # section_pats = []
    url = ''
    table_examples = []
    all_info = {}
    auxiliary_info = {}
    # 私有属性
    __patterns = {}
    __table_pat = re.compile('<table(?:.|\n)*?</table>')
    __tables = []

    def __init__(self, filename, label='重大合同'):
        self.label = label
        self.id = filename
        self.table_examples = copy.deepcopy([])
        self.auxiliary_info = copy.deepcopy({})
        self.__tables = copy.deepcopy([])
        self.all_info = copy.deepcopy(
            {
                'info_num': 0,
                'record': []
            }
        )
        self.url = 'http://www.cninfo.com.cn/xxx'
        # 初始化 pattern
        self.init_pattern()
        # 获得 schema, html, text, table
        self.get_schema()
        self.get_html(filename)
        self.get_text()
        self.get_tables()
        # 抽取流程
        # self.extraction()

    def init_pattern(self):
        self.__patterns = copy.deepcopy({})
        self.__patterns = {
            'table': re.compile('<table(?:.|\n)*?</table>'),
            'title': re.compile('<div title="(.*?)" type="pdf">'),
            'paragraph1': re.compile('<div id="SectionCode_\d" title="(.*?)" type="paragraph">'),
            'paragraph2': re.compile('<div id="SectionCode_\d-\d" title="(.*?)" type="paragraph">'),
            'content': re.compile('<div type="content">((?:.|\n)*?)</div>'),
            'other_tags': re.compile('<[^\u4e00-\u9fa5]*?>'),
        }

    def get_schema(self):
        self.schema = copy.deepcopy({})
        with open(SCHEMA_FILE) as f:
            self.schema = json.loads(f.read())[self.label]

    def get_html(self, filename):
        html_file_path = os.path.join(ROOT, self.label, 'html', filename)
        with open(html_file_path) as f:
            self.html_for_table = f.read()
            for line in f.readlines():
                self.html += line.strip()
        # pdf = os.path.join(ROOT, self.label, 'pdf', filename+'.pdf')
        # self.html = lz_pdf2html(pdf)
        if not self.html:
            self.html = self.html_for_table

    def get_text(self):
        """ html 转 txt, 现在是处理比赛格式，所以需要把标点都改成半角 """
        def title_rpl(matched):
            rpl_from, rpl_to = matched.group(0), clean_sent(matched.group(1))
            rpl_to = 'TITLE:' + rpl_to + '\n'
            temp = re.sub(rpl_from, rpl_to, rpl_from)
            return temp

        def para1_rpl(matched):
            rpl_from, rpl_to = matched.group(0), clean_sent(matched.group(1))
            rpl_to = 'PARA_1:' + rpl_to + '\n'
            temp = re.sub(rpl_from, rpl_to, rpl_from)
            return temp

        def para2_rpl(matched):
            rpl_from, rpl_to = matched.group(0), clean_sent(matched.group(1))
            rpl_to = 'PARA_2:' + rpl_to + '\n'
            temp = re.sub(rpl_from, rpl_to, rpl_from)
            return temp

        def cont_rpl(matched):
            rpl_from, rpl_to = matched.group(0), clean_sent(matched.group(1))
            if rpl_to:
                rpl_to = 'CONTENT:' + rpl_to + '\n'
            else:
                pass
            temp = re.sub(rpl_from, rpl_to, rpl_from)
            return temp

        html = self.__patterns['table'].sub('', self.html)
        html = self.__patterns['title'].sub(title_rpl, html)
        html = self.__patterns['paragraph1'].sub(para1_rpl, html)
        html = self.__patterns['paragraph2'].sub(para2_rpl, html)
        html = self.__patterns['content'].sub(cont_rpl, html)

        html = self.__patterns['other_tags'].sub('', html)

        text = re.sub('\n+[\s\n]*', '\n', html)
        text += 'EOF'
        print(text)
        self.text = html

    def extraction(self):
        pass

    def text_extr(self, _input):
        if isinstance(_input, list):
            result = []
            for item in _input:
                result.append(self.text_extr(item))
            return result
        elif isinstance(_input, str):
            infos = Event_Extr(title='', content=_input, url=self.url, column='', topic=self.label)
            return infos
        else:
            print('[Type error]: 文本抽取类型错误')

    def get_tables(self):
        bs = BeautifulSoup(self.html_for_table, 'lxml')
        tables = bs.find_all('table')

        for table in tables:
            self.__tables.append(table)

        for table in self.__tables:
            table_example = Table(table, self.label)
            if table_example.dic:
                self.table_examples.append(table_example)

    # def get_section(self):
    #
    #     # 添加目录标志
    #     if self.__table_pat.search(self.html):
    #         html = re.sub(self.__table_pat, '', self.html)
    #     else:
    #         html = self.html
    #     find_res = {}
    #     section_levels = []
    #     for tag_idx, tags_pat in enumerate(self.section_pats):
    #         for idx, res in enumerate(tags_pat.findall(html)):
    #             find_res[res] = '<div class="Section{}">{}</div>'.format(tag_idx, res)
    #
    #             if tag_idx not in section_levels:
    #                 section_levels.append("Section{}".format(tag_idx))
    #     for k, v in find_res.items():
    #         html = html.replace('<div>' + k + '</div>', v)
    #
    #     # 按照目录结构切片
    #     section_order = {}
    #     for level in section_levels:
    #         section_order[level] = html.index('<div class="{}">'.format(level))
    #     sorted_key_list = sorted(section_order, key=lambda x: section_order[x])
    #
    #     def html_split(keys, input_html):
    #         if keys[0] in input_html:
    #             results = input_html.split('<div class="{}">'.format(keys[0]))
    #         else:
    #             results = [input_html]
    #         temp = []
    #         if len(keys) > 1:
    #             for result in results:
    #                 temp.append(html_split(keys[1:], result))
    #         else:
    #             temp = results
    #         return temp
    #
    #     sections = html_split(sorted_key_list, html)
    #     self.__section_depth = len(sorted_key_list)
    #     self.__sections = sections
    #
    # def get_section_pats(self):
    #     level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
    #     level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
    #     level3_tags_pat = re.compile('<div>(（[一二三四五六七八九十]+）.+?)</div>')
    #     self.section_pats = [level1_tags_pat, level2_tags_pat, level3_tags_pat]


def main():
    filename = '53536'
    ie = InformationExtraction(filename, '股东增减持')
    print(ie)


if __name__ == '__main__':
    main()
