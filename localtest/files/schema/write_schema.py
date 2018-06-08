# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import json

schema = {
    "股权质押信息": ['股东名称', '是否为第一大股东及一致行动人', '质押股数', '质押开始日期', '解除质押日期', '本次质押占其所持股份比例', '质权人', '用途']
}

print(schema)

with open('股东股权质押事件', 'w') as fo:
    fo.write(json.dumps(schema, ensure_ascii=False, indent=4))