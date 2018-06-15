# -*- coding:UTF-8 -*-
# !/usr/bin/env python3

import re
import copy

from kaggle.InformationExtraction import InformationExtraction
from kaggle.extr import Event_Extr


class ShareholdingChange(InformationExtraction):

    format_table_0 = ''
    format_table_1 = ''
    event_type = ''

    def __init__(self, filename, label='股东增减持'):
        InformationExtraction.__init__(self, filename, label)
        self.classifier()
        self.extraction()
        pass

    def get_section_pats(self):
        level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
        level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
        self.section_pats = [level1_tags_pat, level2_tags_pat]

    def extraction(self):

        # TODO 现在只有减持的转换，后续添加增持

        # 获得表格信息
        self.table_extr()
        self.table_classifier()
        # 表格信息处理
        if self.table_examples:
            self.table_procedure()
        # 文本抽取股东全称和对应的股东简称
        self.name_extr()
        # print(self.all_info)

    def classifier(self):
        increase = self.html.count('增持')
        reduce = self.html.count('减持')
        self.event_type = '增持' if increase > reduce else '减持'

    def table_procedure(self):
        # 第一个表格抽取["股东简称","变动截止日期","变动价格","变动数量",]
        table_0 = self.table_examples[0]
        self.format_table_0 = self.table0(table_0)

        # 第二个表格抽取["股东简称","变动后持股数","变动后持股比例"]
        for table in self.table_examples:
            if table.add_info and table.add_info['type'] == 'table_1':
                self.format_table_1 = self.table1(table)
                break
        # if self.table_examples.__len__() > 1:
        #     table_1 = self.table_examples[1]
        #     self.format_table_1 = self.table1(table_1)
        # 表格信息格式化
        self.format_info()
        # 填入
        for key, values in self.format_table_0.dic.items():
            if self.all_info['record'] and key in self.all_info['record'][0] or key == '变动比例':
                for i, value in enumerate(values):
                    self.all_info['record'][i][key] = value
        # 合并
        last_info = {
            'name': '',
            'num': 0,
            'ratio': 0
        }
        if self.format_table_1:
            for idx, record in enumerate(self.all_info['record']):
                name = record['股东简称']
                if last_info['name'] == name:
                    pass
                else:
                    if name in self.format_table_1.dic['股东简称']:
                        index = self.format_table_1.dic['股东简称'].index(name)
                        last_info['name'] = name
                        last_info['num'] = self.format_table_1.dic['变动前持股数'][index]
                        last_info['ratio'] = self.format_table_1.dic['变动前持股比例'][index]
                    else:
                        print('[error] 股东不在表1中，请检查。')
                # 减持计算结果
                if self.event_type == '减持':
                    record['变动后持股数'] = last_info['num'] - record['变动数量']
                    last_info['num'] = record['变动后持股数']
                    record['变动后持股比例'] = last_info['ratio'] - record['变动比例']
                    last_info['ratio'] = record['变动后持股比例']
                # 增持结果计算
                elif self.event_type == '增持':
                    record['变动后持股数'] = last_info['num'] + record['变动数量']
                    last_info['num'] = record['变动后持股数']
                    record['变动后持股比例'] = last_info['ratio'] + record['变动比例']
                    last_info['ratio'] = record['变动后持股比例']
                else:
                    print('[Error]: 未能成功分类（减持，增持）')

        else:
            print('[warning]: 没有表格1')
        for record in self.all_info['record']:
            record['公告id'] = self.id

    def table_classifier(self):
        table_0_pt = re.compile('(?:.*减持期间.*|.*减持均价.*|.*减持股数.*|.*减持比例.*)')
        table_1_pt = re.compile('(?:.*减持前.*|.*减持后.*|.*股份性质.*)')
        for i, table in enumerate(self.table_examples):
            for k, v in table.dic.items():
                if table_0_pt.search(k):
                    self.table_examples[i].add_info['type'] = 'table_0'
                    break
                elif table_1_pt.search(k):
                    self.table_examples[i].add_info['type'] = 'table_1'
                    break
            else:
                print('[Warning]: 错误的表格类别')
        pass

    def table0(self, table):
        self.all_info['info_num'] += table.info_number
        self.init_record()
        table = self.trans(table)
        return table

    def init_record(self):
        for i in range(self.all_info['info_num']):
            self.all_info['record'].append(copy.deepcopy(self.schema))

    def table1(self, table):
        table = self.trans(table)
        return table

    def trans(self, table):
        """ 与公告类型相关，对于不同公告类型应有不同处理 """
        abbr_pt = re.compile('股东名称')
        time_pt = re.compile('减持[期时]间')
        price_pt = re.compile('减持均价.*')
        reduced_num_pt = re.compile('减持股[数份].*')
        reduced_ratio_pt = re.compile('减持比例.*')

        before_num_pt = re.compile('本次[增减]持前持有股份.*股数')
        before_ratio_pt = re.compile('本次[增减]持前持有股份.*比例')
        after_num_pt = re.compile('本次[增减]持后持有股份.*股数')
        after_ratio_pt = re.compile('本次[增减]持后持有股份.*比例')

        for key in table.dic:
            # table_0
            if abbr_pt.search(key):
                table.dic['股东简称'] = table.dic.pop(key)
                continue
            if time_pt.search(key):
                table.dic['变动截止日期'] = table.dic.pop(key)
                continue
            if price_pt.search(key):
                table.dic['变动价格'] = table.dic.pop(key)
                continue
            if reduced_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                table.dic['变动数量'] = table.dic.pop(key)
                continue
            if reduced_ratio_pt.search(key):
                table.dic['变动比例'] = table.dic.pop(key)
                continue
            # table_1
            if before_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                table.dic['变动前持股数'] = table.dic.pop(key)
                continue
            if before_ratio_pt.search(key):
                table.dic['变动前持股比例'] = table.dic.pop(key)
                continue
            if after_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                table.dic['变动后持股数'] = table.dic.pop(key)
                continue
            if after_ratio_pt.search(key):
                table.dic['变动后持股比例'] = table.dic.pop(key)
                continue
            print('[warning]不需要或无法识别的键：{}'.format(key))
        return table

    def format_info(self):
        comma = re.compile(',')
        ten_thousand = re.compile('万')
        percent = re.compile('%')

        # 股份数量
        def format_number(num):
            num = comma.sub('', num)
            multiple = 1
            if ten_thousand.search(num):
                num = ten_thousand.sub('', num)
                multiple *= 10000
            num = float(num)
            num *= multiple
            num = int(num)
            return num

        # 股份比例
        def format_ratio(num):
            num = percent.sub('', num)
            multiple = 0.01
            num = float(num)
            num *= multiple
            return num

        # 表格0
        for key, values in self.format_table_0.dic.items():
            if key == '变动数量' or key == '变动后持股数' or key == '变动前持股数':
                for i, v in enumerate(values):
                    values[i] = format_number(v)
            elif key == '变动比例' or key == '变动后持股比例' or key == '变动前持股比例':
                for i, v in enumerate(values):
                    values[i] = format_ratio(v)

        # 表格1
        if self.format_table_1:
            for key, values in self.format_table_1.dic.items():
                if key == '变动数量' or key == '变动后持股数' or key == '变动前持股数':
                    for i, v in enumerate(values):
                        values[i] = format_number(v)
                elif key == '变动比例' or key == '变动后持股比例' or key == '变动前持股比例':
                    for i, v in enumerate(values):
                        values[i] = format_ratio(v)

    def name_extr(self):
        """ 抽取股东全称和股东简称 """
        temp = re.sub('<.*?>', '', self.html)
        name_pt = re.compile('股东(?P<name>(?:[\u4e00-\u9fa5]+公司|[\w\s]+))[(（]以下简称["“]?(?P<abbr>(?:[\u4e00-\u9fa5]+|[\w\s]+))["”][)）]')
        # name_pt = re.compile('股东RICH GOAL HOLDINGS LIMITED（以下简称“RICH GOAL”）')
        res = name_pt.search(temp)
        space_pt = re.compile('')

        if res:
            for i, record in enumerate(self.all_info['record']):
                name = re.sub('\s', '', res.group('name'))
                abbr = re.sub('\s', '', res.group('abbr'))
                if record['股东简称'] == name or record['股东简称'] == abbr:
                    record['股东全称'] = res.group('name')
                    record['股东简称'] = res.group('abbr')
        for i, record in enumerate(self.all_info['record']):
            if record['股东简称'] and not record['股东全称']:
                record['股东全称'], record['股东简称'] = record['股东简称'], ''


if __name__ == '__main__':

    SC = ShareholdingChange('10243', label='股东增减持')
    print(SC)
