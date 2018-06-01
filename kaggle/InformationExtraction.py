# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import json
import re

from bs4 import BeautifulSoup

from kaggle.extr import Event_Extr
from kaggle.Table import Table
from kaggle.LzPdf2Html.create_new_html import lz_pdf2html

SCHEMA_FILE = 'schema/schema.json'


class InformationExtraction:

    with open(SCHEMA_FILE) as f:
        schema = json.loads(f.read())

    table_pat = re.compile('<table.+?</table>')

    level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
    level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
    level3_tags_pat = re.compile('<div>(（[一二三四五六七八九十]+）.+?)</div>')

    tags_pats = [level1_tags_pat, level2_tags_pat, level3_tags_pat]

    def __init__(self, filename, lable='重大合同'):

        self.html = self.pdf2html(filename)
        self.label = lable
        self.url = 'http://www.cninfo.com.cn/xxx'
        # self.sections, self.section_depth = self.get_section()
        self.all_info = self.extraction()

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
        html = re.sub(self.table_pat, '', self.html)
        find_res = {}
        section_levels = []
        for tag_idx, tags_pat in enumerate(self.tags_pats):
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

    def pdf2html(self, filename):
        html = lz_pdf2html(filename)
        return html

    @staticmethod
    def read_file(filename):
        with open(filename) as f:
            return f.read()


def main():
    filename = 'data/重大合同/2379.pdf'
    ie = InformationExtraction(filename)
    print(ie)


if __name__ == '__main__':
    main()
