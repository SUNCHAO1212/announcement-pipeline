# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import absolute_import, unicode_literals, print_function

import sys



from scrapy.loader import ItemLoader
from scrapy.item import Item, Field
from w3lib.html import remove_tags
from scrapy.loader.processors import TakeFirst, Compose, Join
from HTMLParser import HTMLParser
import base64, jsonpath
from lxml.html.clean import Cleaner
import json, re
from collections import defaultdict
from scrapy.selector import Selector
from datetime import datetime


class EventPickles():
    def __init__(self, extr_tmpl):
        self.loop_xpath = extr_tmpl.get('selectors', None).get('loopXPath', None)
        self.fields = extr_tmpl.get('selectors', None).get('fields', None)
        self.total_result = defaultdict(dict)
        self.event_type = extr_tmpl.get('eventInfo', None).get('eventType', None)
        for field in self.fields:
            self.total_result[field['id']]['idTypeCn'] = field['idTypeCn']
            self.total_result[field['id']]['idRoleCn'] = field['idRoleCn']
            self.total_result[field['id']]['required'] = field['required']

        self.text_extr_pat = {}
        for field in self.fields:
            self.text_extr_pat[field['id']] = field.get('textPattern', [])

    def parse_item(self, html):
        hxs = Selector(text=html)
        for e in hxs.xpath(self.loop_xpath or '(//*)[1]'):
            item = Item()
            loader = ItemLoader(item, selector=e)

            for field in self.fields:
                name = field['id']
                item.fields[name] = Field()

                rules = field['selector']
                self.get_details(name, rules, loader)
            else:
                return loader.load_item()

    def convert_type(self, infs):
        def _wrapper(inf, t):
            def _convert(data):
                if t not in ['join', 'list'] and isinstance(data, list):
                    data = Join()(data) # 控制获取数据方式
                    if type(data) in [str]:
                        data = data.strip()
                    elif type(data) in [int, float, datetime]:
                        data = str(data)
                    else:
                        return data

                if t == 'join':
                    sep = inf.get('sep', u' ')
                    return Join(sep)(data).strip()
                elif t == 'list':
                    sep = inf.get('sep', u' ')
                    return remove_tags(Join(sep)(data)).strip()
                elif t == 'text':
                    return remove_tags(data).strip()
                elif t == 'clean':
                    cleaner = Cleaner(style=True, scripts=True, javascript=True, links=True, meta=True)
                    return cleaner.clean_html(data)
                elif t == 'unesc':
                    return HTMLParser().unescape(data)
                elif t == 'base64':
                    return base64.decodestring(data)
                elif t == 'sub':
                    frm = inf.get('from')
                    to = inf.get('to')
                    return re.sub(frm, to, data)
                elif t == 'jpath':
                    qs = inf.get('query')
                    return jsonpath.jsonpath(json.loads(data), qs)
                elif t == 'map':
                    m = inf.get('map')
                    d = inf.get('default')
                    return m.get(data, d)
                elif t == 'int':
                    return int(float(data))
                elif t == 'float':
                    return float(data)
                elif t == 'date':
                    fmt = inf.get('fmt', 'auto')
                    tz = inf.get('tz', '+00:00')
                    return self.parse_date(data, fmt, tz)
                # FIXME: remove `utc`
                elif t == 'utc' or t == 'cst':
                    fmt = inf.get('fmt', 'auto')
                    return self.parse_date(data, fmt, '+08:00')
                else:
                    return data

            return _convert

        infs = infs if type(infs) == list else [infs]
        return Compose(*[_wrapper(inf, inf.get('type', 'str')) for inf in infs])

    def get_details(self, name, rules, loader, others=None):
        for v in rules['rules']:
            if 'value' in v:
                add_v_x = loader.add_value
                v_x = v.get('value')
            elif 'xpath' in v:
                add_v_x = loader.add_xpath
                v_x = v.get('xpath')

            add_v_x(
                name,
                v_x,
                self.convert_type(v.get('parse', {})),
                re=v.get('regex')
            )

    def text_extr(self, scrapy_result=None):

        result = defaultdict(dict)

        for k, v in scrapy_result.items():
            vv = v
            result[k]['value'] = []

            for rule in self.text_extr_pat[k]:
                xx_find_result = []

                if 'findall' in rule:
                    for xx_find in rule['findall']:
                        for vvv in vv:
                            for w in re.compile(xx_find['regex']).findall(vvv):
                                if w.strip():
                                    xx_find_result.append(w)
                                    # 为啥extend又不行了
                            # xx_find_result.extend([w for w in re.compile(xx_find['regex']).findall(vvv) if w.strip()])
                    vv = xx_find_result

                elif 'search' in rule:
                    for xx_find in rule['search']:
                        for vvv in vv:
                            w = re.compile(xx_find['regex']).search(vvv)
                            if w:
                                if w.group():
                                    xx_find_result.append(w.group())
                    vv = xx_find_result

                elif 'filter_p' in rule:
                    vv = [vvv.strip() for vvv in vv if re.compile(rule['filter_p']['regex']).match(vvv) and vvv.strip()]

                elif 'replace' in rule:
                    vv = [re.compile(rule['replace']['regex'][0]).sub(rule['replace']['regex'][1], vvv).strip() for vvv in vv if vv]

                # elif 'split' in rule:
                #     for xx_find in rule['split']:
                #         for vvv in vv:
                #             w = re.compile(xx_find['regex']).split(vvv)
                #             if w:
                #                 xx_find_result.append(w)
                #     vv = xx_find_result
                elif 'split' in rule:
                    vv_tmp = []
                    for vvv in vv:
                        for vvv_tmp in re.compile(rule['split']['regex']).split(vvv):
                            if vvv_tmp:
                                vv_tmp.append(vvv_tmp.strip())
                    vv = vv_tmp
                elif 'filter' in rule:
                    vv = [vvv.strip() for vvv in vv if not re.compile(rule['filter']['regex']).match(vvv) and vv]

            result[k]['value'].append([vt for vt in set(vv)])

            if k not in result:
                result[k]['value'].append(v)

            result[k].update(self.total_result[k])

        result['externalInfo']['eventType'] = self.event_type

        return result
