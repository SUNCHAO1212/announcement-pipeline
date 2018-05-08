# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import absolute_import, unicode_literals, print_function

import sys,os



import json
import re
import codecs
from collections import defaultdict
from localtest.event_extr.event_extr import event_extr_main

zhaohui_list = [
    "http://www.cqn.com.cn/ms/content/.*",
    "http://tbt.testrust.com/recalls/.*",
    "http://www.nbtsc.cn:80/klzh/.*",
    "http://www.ziq.gov.cn/portal/chnl16978/.*",#中国贸易救济信息网
    "http://www.gzwto.gov.cn/info/recall/.*", #广州市技术性贸易措施综合服务平台
    "http://www.cacs.mofcom.gov.cn/cacs/newcommon/details.aspx\\?navid=A09.*", #东莞市WTO/TBT预警信息平台
    "http://www.cacs.gov.cn/cacs/newcommon/details.aspx\\?navid=A09&articleId=\\d+",
    "http://www.spsp.gov.cn/DataCenter/Recall/RecallDetail.aspx.*" #浙江省标准信息与质量安全公共科技创新服务平台
]
# TBT_list = [
#     "http://www.tbt-sps.gov.cn/tbtTbcx/getTbcxContent.action\\?mid=\\d+&TBType=\\d+",
#     "http://www.cnnbzj.com/cn/wtotbt/tbtDetail_\\d+.html",
#     "http://www.tbtguide.com/bzhyjy/tbzx1/tbttb/.*",
#     "http://www.nbtsc.cn:\\d+/tbtofficial/\\d+.jhtml",
#     "http://www.tbt-sps.ziq.gov.cn/portal/tbttb/\\d+.htm"
# ]
# SPS_list = [
#     "http://www.tbt-sps.gov.cn/tbcx/.*",
#     "http://www.nbtsc.cn:80/spsofficial/.*",
#     "http://www.tbt-sps.ziq.gov.cn/portal/spstb/.*",
# ]




def Event_Extr(title,content,url,column,topic):
    try:
        js = {
            "title":title,
            "content":content,
            "url":url,
            "column":column,
            "topic":topic,
        }

        for item in zhaohui_list:
            if re.compile(item).match(js["url"]):
                js["url"] = "召回扣留"
        js["url"] = js["url"]+"_"+js["column"]+"_"+js["topic"]
        event_extr = event_extr_main(json.dumps(js))
        if event_extr:
            event_extr = json.loads(event_extr)

            #整理输出格式
            events = defaultdict(list)
            for k,v in event_extr["event"].items():
                if "idTypeCn" in v:
                    events[v["idTypeCn"]].append(v)

            # #添加type字段
            # for item in TBT_list:
            #     if re.compile(item).match(js["url"]):
            #         events["type"] = "TBT通报"
            #
            # for item in SPS_list:
            #     if re.compile(item).match(js["url"]):
            #         events["type"] = "SPS通报"
            #
            # if js["url"] == "召回扣留":
            #     events["type"] = js["url"]
            events["type"] = js["topic"]

            return json.dumps(events,ensure_ascii=False)

        else:
            msg = {
                "success":"false",
                "msg":"ysq_log: There is no matching template!!!",
            }
            return json.dumps(msg,ensure_ascii=False)

    except Exception as e:
        msg = {
            "success":"false",
            "msg":str(e),
        }
        return json.dumps(msg, ensure_ascii=False)


if __name__ =="__main__":
    test={
        'title':'美国召回疑含阪崎肠杆菌的萨米婴儿牛奶',
        'content':'''
<div class="content" id="article">\r\n\t      据<a href="http://news.foodmate.net/tag_2463.html" class="zdbq" target="_blank">美国</a>食品药品<a href="http://news.foodmate.net/tag_4604.html" class="zdbq" target="_blank">管理</a>局消息，9月30日美国食品药品管理局发布<a href="http://news.foodmate.net/tag_2357.html" class="zdbq" target="_blank">召回</a>通告称，Graceleigh, Inc. 公司宣布召回萨米<a href="http://news.foodmate.net/tag_3731.html" class="zdbq" target="_blank">婴儿</a><a href="http://news.foodmate.net/tag_1336.html" class="zdbq" target="_blank">牛奶</a>（Sammy's Milk ），因为产品可能含有<a href="http://news.foodmate.net/tag_82.html" class="zdbq" target="_blank">阪崎肠杆菌</a>，而且铁含量不足，对婴儿健康构成威胁。\r\n\t<div style="text-align:center;">\r\n\t\t<img src="http://file1.foodmate.net/file/news/201610/13/10-36-36-92-543665.jpg" alt="羊奶粉" width="262" height="500">\r\n\t</div>\r\n\t<div>\r\n\t\t \r\n\t</div>\r\n\t<div>\r\n\t\t    这款产品的规格为12.84盎司，装于塑料桶内，有效期至2016年11月-2018年8月。\r\n\t</div>\r\n\t<div>\r\n\t\t \r\n\t</div>\r\n\t<div>\r\n\t\t    产品已被销往母婴市场零售商，而且也通过网上销售。截止目前尚未出现婴儿染病的报告。\r\n\t</div>\r\n\t<div>\r\n\t\t \r\n\t</div>\r\n\t<div>\r\n\t\t    美国FDA表示，这款产品被定义为婴儿配方食品进行销售，然而并不符合婴儿配方食品相关条例，无阪崎肠杆菌检测合格证明，而且铁含量不足但未标明。\r\n\t</div>\r\n\t<div>\r\n\t\t \r\n\t</div>\r\n\t<div>\r\n\t\t    原文链接：http://www.fda.gov/Safety/Recalls/ucm523489.htm\r\n\t</div>\r\n</div>
        ''',
        'url':'http://www.tbtsps.cn/page/tradez/Warnewscontent.action?id=16747&lm=006001&hy=54',
        'column':'风险预警',
        'topic':'召回'
    }
    print(Event_Extr(test['title'],test['content'],test['url'],test['column'],test['topic']))
