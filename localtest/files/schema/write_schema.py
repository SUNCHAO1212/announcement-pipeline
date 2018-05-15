# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import json

schema = {
    "主体信息":['股东名称', '股东身份', '持股数量', '持股比例', '股份来源'],
    "减持计划":['股东名称', '计划减持数量', '计划减持比例', '减持期间', '减持方式', '减持合理价格区间', '拟减持股份来源', '拟减持原因']
}

print(schema)

with open('股东减持计划事件'+'.json', 'w') as fo:
    fo.write(json.dumps(schema, ensure_ascii=False))