# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import re

from kaggle.InformationExtraction import InformationExtraction


class ShareholdingChange(InformationExtraction):
    def __init__(self, pdf, label='股东增减持'):
        InformationExtraction.__init__(self, pdf, label)
        pass

    def get_section_pats(self):
        level1_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')
        level2_tags_pat = re.compile('<div>([1234567890]+、.+?)</div>')
        self.section_pats = [level1_tags_pat, level2_tags_pat]


SC = ShareholdingChange('股东增减持_1268061.pdf')
print(SC)