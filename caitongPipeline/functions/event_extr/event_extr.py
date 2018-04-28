# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import absolute_import, unicode_literals, print_function

import codecs
import json
import os
import re
from collections import defaultdict

from functions.event_extr.event_engine import EventPickles

TMPL_PATH = 'functions/tmpl/'
file=codecs.open('temple.txt','w','utf8')

def load_tmpl():
    tmpls = defaultdict(list)
    for parent, _, files in os.walk(TMPL_PATH):
        for file in files:
            extr_tmpl = json.load(codecs.open(os.path.join(parent, file), 'rb', 'utf8'))
            tmpl = {
                "name":str(file).split(".")[0],
                "template":EventPickles(extr_tmpl),
                "field":extr_tmpl["selectedField"]
            }
            tmpls[re.compile(extr_tmpl['feature'])].append(tmpl)
    return tmpls

def sel_valid_tmpl_second(tmpls, crawl_doc_url):
    for k, v in tmpls.items():
        if k.match(crawl_doc_url):
            return v[0]
    return None

tmpls = load_tmpl()

def event_extr_main(content):
    json_msg = json.loads(content)
    #挑选模板
    tmpl = sel_valid_tmpl_second(tmpls, json_msg["url"])
    if tmpl:
        name = tmpl["name"]
        file.write(name+'\r')
        epickles = tmpl["template"]
        field = tmpl["field"]

        #根据模板名称挑选字段
        # config = ConfigParser.ConfigParser()
        # config.read("info.cfg")
        # field=config.get('template_field',name.encode("utf-8"))

        if field == "title_content":
            text = "<liangzhi_title>" + json_msg["title"] + "</liangzhi_title><liangzhi_content>" + json_msg["content"] +"</liangzhi_content>"
        else:
            text = json_msg[field]

        #根据挑选的模板解析字段
        scrapy_result = epickles.parse_item(text)

        z = epickles.text_extr(scrapy_result)

        json_msg.update({'event': z})

        return json.dumps(json_msg)
    else:
        return None