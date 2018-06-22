# -*- coding:UTF-8 -*-
# !/usr/bin/env python3

import re
import copy
import calendar

from kaggle.InformationExtraction import InformationExtraction
from kaggle.extr import Event_Extr


space_pt = re.compile('\s+')


def clean_sent(sent):
    sent = space_pt.sub('', sent)
    return sent


class ShareholdingChange(InformationExtraction):

    format_table_0 = ''
    format_table_1 = ''
    event_type = ''

    def __init__(self, filename, label='股东增减持'):
        InformationExtraction.__init__(self, filename, label)
        self.classifier()
        self.extraction()
        pass

    def classifier(self):
        increase = self.html.count('增持')
        reduce = self.html.count('减持')
        self.event_type = '增持' if increase > reduce else '减持'

    def get_section_pats(self):
        level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
        level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
        self.section_pats = [level1_tags_pat, level2_tags_pat]

    def extraction(self):
        # 文本抽取股东全称和对应的股东简称
        self.name_extr()
        # 获得表格信息
        # self.table_extr()
        self.table_classifier()
        # 表格信息处理
        if self.table_examples:
            self.table_procedure()
        # 全信息格式化
        self.format_all_info()
        # print(self.all_info)

    def name_extr(self):
        """ 抽取股东全称和股东简称 """
        self.auxiliary_info['name'] = copy.deepcopy([])
        # 转为纯文本，后续可以加到父类中进行
        temp = re.sub('<.*?>', '', self.html)
        temp = clean_sent(temp)

        name_pt_1 = re.compile('(?:接到|股东)(?P<name>[\u4e00-\u9fa5（）()]+(?:公司|（有限合伙）))[(（]以?下简?称["“]?(?P<abbr>[\u4e00-\u9fa5]+)["”]')
        name_pt_2 = re.compile('股东[\u4e00-\u9fa5()（）""“”]+[和、](?P<name>[\u4e00-\u9fa5]+(?:公司|企业（有限合伙）))[(（]以?下简?称["“]?(?P<abbr>[\u4e00-\u9fa5]+)["”]')
        name_pt_en = re.compile('股东(?P<name>[\w\s]+)[(（]以?下简?称["“]?(?P<abbr>[\w\s]+)["”]')

        res_1 = name_pt_1.search(temp)
        res_2 = name_pt_2.search(temp)
        res_en = name_pt_en.search(temp)

        if res_1:
            self.auxiliary_info['name'].append({
                'name': res_1.group('name'),
                'abbr': res_1.group('abbr')
            })
        if res_2:
            self.auxiliary_info['name'].append({
                'name': res_2.group('name'),
                'abbr': res_2.group('abbr')
            })
        if res_en:
            self.auxiliary_info['name'].append({
                'name': res_en.group('name'),
                'abbr': res_en.group('abbr')
            })

        for name_item in self.auxiliary_info['name']:
            name_item['name'] = clean_sent(name_item['name'])
            name_item['abbr'] = clean_sent(name_item['abbr'])

    def date_extr(self):
        # TODO 文本抽取时间，与表格对应
        pass

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
                print('[Warning] 错误的表格类别')
                self.table_examples[i].add_info['type'] = ''
        pass

    def table_procedure(self):
        # TODO 只有第二种表格没有第一种表格
        # 第一个表格抽取["股东简称","变动截止日期","变动价格","变动数量",]
        # 第二个表格抽取["股东简称","变动后持股数","变动后持股比例"]
        for table in self.table_examples:
            if table.add_info and table.add_info['type'] == 'table_1':
                self.format_table_1 = self.table1(table)
            elif table.add_info and table.add_info['type'] == 'table_0':
                self.format_table_0 = self.table0(table)
        # if self.table_examples.__len__() > 1:
        #     table_1 = self.table_examples[1]
        #     self.format_table_1 = self.table1(table_1)
        # 表格信息格式化
        self.format_info()
        # 填入
        if self.format_table_0:
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
                    elif name.find(self.format_table_1.dic['股东简称'][0]) >= 0:
                        index = 0
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

    def table0(self, table):
        self.all_info['info_num'] += table.info_number
        self.init_record(table.info_number)
        table = self.pre_format(table)
        return table

    def init_record(self, info_number):
        for i in range(info_number):
            self.all_info['record'].append(copy.deepcopy(self.schema))

    def table1(self, table):
        table = self.pre_format(table)
        return table

    def pre_format(self, table):
        """ 与公告类型相关，对于不同公告类型应有不同处理 """
        abbr_pt = re.compile('(?:股东名称|股东姓名|减持股东)')
        time_pt = re.compile('[增减]持[期时]间')
        price_pt = re.compile('[增减]持(?:均价|价格区间).*')
        reduced_num_pt = re.compile('[增减]持(?:股份|股数|数量).*')
        reduced_ratio_pt = re.compile('(?:[增减]持|占.*总股本).*比例.*')

        before_num_pt = re.compile('^.*[增减]持.*前.*(?:股份|持).*(?:股份?数|持有股份|数量)[^比例]*$')
        before_ratio_pt = re.compile('^.*[增减]持.*前.*(?:股份|持).*(?:占总股本|比例).*$')
        after_num_pt = re.compile('^.*[增减]持.*后.*(?:股份|持).*(?:股份?数|持有股份|数量)[^比例]*$')
        after_ratio_pt = re.compile('^.*[增减]持.*后.*(?:股份|持).*(?:占总股本|比例).*')

        temp_dict = copy.deepcopy({})
        for key in table.dic:
            # table_1
            if before_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                # table.dic['变动前持股数'] = table.dic.pop(key)
                temp_dict['变动前持股数'] = table.dic[key]
                continue
            if before_ratio_pt.search(key):
                # table.dic['变动前持股比例'] = table.dic.pop(key)
                temp_dict['变动前持股比例'] = table.dic[key]
                continue
            if after_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                # table.dic['变动后持股数'] = table.dic.pop(key)
                temp_dict['变动后持股数'] = table.dic[key]
                continue
            if after_ratio_pt.search(key):
                # table.dic['变动后持股比例'] = table.dic.pop(key)
                temp_dict['变动后持股比例'] = table.dic[key]
                continue
            # table_0
            if abbr_pt.search(key):
                # 将所有的股东名称都以股东简称代替，方便后续操作，并且此处进行简单的纠正过程
                # table.dic['股东简称'] = table.dic.pop(key)
                temp_dict['股东简称'] = table.dic[key]
                for i, name in enumerate(temp_dict['股东简称']):
                    for item in self.auxiliary_info['name']:
                        if item['abbr'].find(name) >= 0:
                            temp_dict['股东简称'][i] = name
                            break
                        elif item['name'].find(name) >= 0:
                            temp_dict['股东简称'][i] = item['abbr']
                            item['name'] = name
                            break
                        else:
                            pass
                    else:
                        print('[Warning] 股东未匹配:{}/{}'.format(name, self.auxiliary_info['name']))
                continue
            if time_pt.search(key):
                # table.dic['变动截止日期'] = table.dic.pop(key)
                temp_dict['变动截止日期'] = table.dic[key]
                continue
            if price_pt.search(key):
                # table.dic['变动价格'] = table.dic.pop(key)
                temp_dict['变动价格'] = table.dic[key]
                continue
            if reduced_ratio_pt.search(key):
                # 先匹配减持比例，防止被覆盖
                # table.dic['变动比例'] = table.dic.pop(key)
                temp_dict['变动比例'] = table.dic[key]
                continue
            if reduced_num_pt.search(key):
                # 将 key 固定，倍数或单位放到 value 中处理
                if re.search('.*万股.*', key):
                    for i in range(len(table.dic[key])):
                        table.dic[key][i] += '万'
                # table.dic['变动数量'] = table.dic.pop(key)
                temp_dict['变动数量'] = table.dic[key]
                continue

            print('[Warning] 不需要或无法识别的键：{}'.format(key))
            temp_dict[key] = table.dic[key]

        table.dic = temp_dict
        return table

    def format_info(self):
        comma = re.compile('[,，]')
        ten_thousand = re.compile('万')
        percent = re.compile('%')

        # 股份数量
        def format_number(num):
            num = re.sub('股', '', num)
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
        if self.format_table_0:
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

    def format_all_info(self):

        def format_float(ratio, n):
            return round(ratio, n)

        def format_date(date):

            pt1 = re.compile('.*(?P<year>\d{4})年.*(?P<month>\d+)月(?:(?P<day>\d+)日)?')
            pt2 = re.compile('.*(?P<year>\d{4}).*[.-](?P<month>\d+)[.-](?P<day>\d+)')
            pt3 = re.compile('.*(?P<year>\d{4}).*[\/](?P<month>\d+)[\/](?P<day>\d+)')
            pt4 = re.compile('\d{8}')

            res1 = pt1.search(date)
            res2 = pt2.search(date)
            res3 = pt3.search(date)
            res4 = pt4.search(date)

            year, month, day = 0, 0, 0

            if res1:
                if res1.group('year'):
                    year = int(res1.group('year'))
                month = int(res1.group('month'))
                if res1.group('day'):
                    day = int(res1.group('day'))
            elif res2:
                if res2.group('year'):
                    year = int(res2.group('year'))
                month = int(res2.group('month'))
                if res2.group('day'):
                    day = int(res2.group('day'))
            elif res3:
                year = int(res3.group('year'))
                month = int(res3.group('month'))
                if res3.group('day'):
                    day = int(res3.group('day'))
                else:
                    day = 0
            elif res4:
                temp = res4.group()
                year = int(temp[0:4])
                month = int(temp[4:6])
                day = int(temp[6:8])
            else:
                print('[Error] 错误的日期')
            # 只有年月
            if day == 0:
                _, day = calendar.monthrange(year, month)

            date = '%4d-%02d-%02d' % (year, month, day)
            return date

        def format_price(price):
            res = re.search('^.*?([\d\\.]+).*$', price)
            # print(res.group(1))
            return res.group(1)

        for idx, record in enumerate(self.all_info['record']):
            # 公告id 格式化
            record['公告id'] = self.id
            # 股东名称 格式化
            for i, name_dict in enumerate(self.auxiliary_info['name']):
                if record['股东简称'] == name_dict['name'] or record['股东简称'] == name_dict['abbr']:
                    record['股东全称'] = name_dict['name']
                    record['股东简称'] = name_dict['abbr']
                    break
                else:
                    pass
            else:
                # 没有匹配的股东名称
                record['股东全称'], record['股东简称'] = record['股东简称'], ''
            # 比例 格式化
            if record['变动比例']:
                record['变动比例'] = format_float(record['变动比例'], 4)
            if record['变动后持股比例']:
                record['变动后持股比例'] = format_float(record['变动后持股比例'], 4)
            # 价格 格式化
            if record['变动价格']:
                record['变动价格'] = format_price(record['变动价格'])
            # 日期格式化
            if record['变动截止日期']:
                record['变动截止日期'] = format_date(record['变动截止日期'])
            pass
        for idx, record in enumerate(self.all_info['record']):
            for k, v in record.items():
                if v == []:
                    record[k] = ''

    def __del__(self):
        # print('析构函数')
        pass


if __name__ == '__main__':

    SC = ShareholdingChange('10243', label='股东增减持')
    print(SC)
