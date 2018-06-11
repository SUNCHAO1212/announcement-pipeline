# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import json
import re
import os
from bs4 import BeautifulSoup

from kaggle.extr import Event_Extr
from kaggle.Table import Table
from kaggle.LzPdf2Html.create_new_html import lz_pdf2html

SCHEMA_FILE = 'schema/schema.json'
ROOT = 'data'


class InformationExtraction:
    # 定义基本属性
    label = ''
    id = ''
    schema = {}
    html = ''
    html_for_table = ''
    section_pats = []
    url = ''
    all_info = {}
    # 私有属性
    __table_pat = re.compile('<table.+?</table>')
    __tables = []
    __sections = []
    __section_depth = 0

    def __init__(self, filename, label='重大合同'):
        self.label = label
        self.id = filename
        self.get_schema()
        self.get_html(filename)
        self.get_section_pats()
        self.url = 'http://www.cninfo.com.cn/xxx'
        # 分段处理
        self.__sections, self.__section_depth = self.get_section()
        pass

    def get_schema(self):
        with open(SCHEMA_FILE) as f:
            self.schema = json.loads(f.read())[self.label]

    def get_html(self, filename):
        pdf = os.path.join(ROOT, self.label, 'pdf', filename+'.pdf')
        self.html = lz_pdf2html(pdf)
        html = os.path.join(ROOT, self.label, 'html', filename+'.html')
        with open(html) as f:
            self.html_for_table = f.read()

    def get_section_pats(self):
        level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
        level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
        level3_tags_pat = re.compile('<div>(（[一二三四五六七八九十]+）.+?)</div>')
        self.section_pats = [level1_tags_pat, level2_tags_pat, level3_tags_pat]

    def extraction(self):

        # def section_extr(sections):
        #     output = []
        #     if isinstance(sections, list):
        #         for section in sections:
        #             output.append(section_extr(section))
        #     else:
        #         output = Event_Extr(title='', content=sections,
        #                             url=self.url, column='', topic=self.label)
        #     return output
        # self.all_info = section_extr(self.sections)
        # TODO 文本合并策略
        output = Event_Extr(title='', content=self.html,
                            url=self.url, column='', topic=self.label)
        print("Information:\n{}".format(output))
        return output

    def get_section(self):

        # 添加目录标志
        html = re.sub(self.__table_pat, '', self.html)
        find_res = {}
        section_levels = []
        for tag_idx, tags_pat in enumerate(self.section_pats):
            for idx, res in enumerate(tags_pat.findall(html)):
                find_res[res] = '<div class="Section{}">{}</div>'.format(tag_idx, res)

                if tag_idx not in section_levels:
                    section_levels.append("Section{}".format(tag_idx))
        for k, v in find_res.items():
            html = html.replace('<div>' + k + '</div>', v)

        # 按照目录结构切片
        section_order = {}
        for level in section_levels:
            section_order[level] = html.index('<div class="{}">'.format(level))
        sorted_key_list = sorted(section_order, key=lambda x: section_order[x])

        def html_split(keys, input_html):
            if keys[0] in input_html:
                results = input_html.split('<div class="{}">'.format(keys[0]))
            else:
                results = [input_html]
            temp = []
            if len(keys) > 1:
                for result in results:
                    temp.append(html_split(keys[1:], result))
            else:
                temp = results
            return temp

        sections = html_split(sorted_key_list, html)
        # self.section_depth = len(sorted_key_list)
        return sections, len(sorted_key_list)

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

    def table_extr(self):
        for table in self.__tables:
            table_example = Table(table, self.label)

    def filter_table(self):
        bs = BeautifulSoup(self.html_for_table, 'lxml')
        tables = bs.find_all('table')
        for table in tables:
            # TODO 保留需要的表格
            if table:
                self.__tables.append(table)
            else:
                print('Not useful table.')


def main():
    filename = '2379'
    ie = InformationExtraction(filename, '重大合同')
    print(ie)


if __name__ == '__main__':
    main()
