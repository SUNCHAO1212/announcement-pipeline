# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import json


with open('schema.json', 'w') as fo:
    temp = {
        '股东增减持':
            {
                '公告id': [],
                '股东全称': [],
                '股东简称': [],
                '变动截止日期': [],
                '变动价格': [],
                '变动数量': [],
                '变动后持股数': [],
                '变动后持股比例': []
            },
        '重大合同':
            {
                '公告id': [],
                '甲方': [],
                '乙方': [],
                '项目名称': [],
                '合同名称': [],
                '合同金额上限': [],
                '合同金额下限': [],
                '联合体成员': [],
            },
        '定向增发': {},
    }
    fo.write(json.dumps(temp, ensure_ascii=False, indent=4))