# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import codecs
import logging.config
import os
import re
import shutil
import subprocess
import time

import numpy as np
from scrapy import Selector

from localtest.LzPdf2Html.find_roi import *

logging.config.fileConfig('logging_info.ini')
logger = logging.getLogger('LzPDFParse')

csspat = re.compile('^\.(.+){.+?([-\d\.]+)px;}$')
xpat = re.compile('(x[\da-z]+)')
ypat = re.compile('(y[\da-z]+)')
xfpat = re.compile('x([\da-z\.]+)')
yfpat = re.compile('y([\da-z\.]+)')
hpat = re.compile('(h[\da-z]+)')
wpat = re.compile('(w[\da-z]+)')
tableheadpat = re.compile('<lz data-tab="table-.+?">')
divc = re.compile('^<div class="c .+?">')
divt = re.compile('^')

just_digit_pat = re.compile('^\d+$')

DEBUG = True

PREFIX = 'myResultHtml'


########
# pdf2html预处理
########
def getPdf2htmlex(filepath, tmpdir):
    return subprocess.call(
        "pdf2htmlEX --optimize-text 1 --use-cropbox 0 --printing 0 --space-as-offset 1 --process-nontext 1 --css-filename lz.css --outline-filename lz.outline --embed-cs 0 --embed-font 0 --svg-embed-bitmap 0 --embed-javascript 0 --embed-outline 0 --embed-external-font 0 --embed-image 0 --process-outline 1 --dest-dir " + tmpdir + " " + filepath + " lz.html",
        shell=True)


#######
# 提取提纲
######
def getOutline(tmpdir):
    buf = []
    with codecs.open(os.path.join(tmpdir, 'lz.outline'), 'rb', 'utf8') as f:
        for l in f.readlines():
            l = l.strip()
            buf.append(l)
    buf = ''.join(buf)

    outlinemap = {}

    hxs = Selector(text=buf)

    hxs = hxs.xpath('/html/body')

    def extractOutline(hxs, level, prefix='Section'):
        for idx, x in enumerate(hxs.xpath('./ul/li'), 1):
            res = x.xpath('./a/text()').extract()
            if res:
                outlinemap[re.compile('<div>' + res[0] + '</div>')] = '<div class="' + prefix + '_' + str(idx) + '">' + \
                                                                      res[0] + '</div>'

            extractOutline(x, level + 1, prefix + '_' + str(idx))

    extractOutline(hxs, 0)

    if DEBUG:
        with codecs.open(os.path.join(tmpdir, 'lz.outline.parse'), 'wb', 'utf8') as f:
            for k, v in outlinemap.items():
                f.write('{}\t{}\n'.format(k, v))

    return outlinemap


#######
# 提取css样式
#####
def getCss(tmpdir):
    allcss = {}
    with codecs.open(os.path.join(tmpdir, 'lz.css'), 'rb', 'utf8') as f:
        for l in f.readlines():
            l = l.strip()
            res = csspat.findall(l)
            if res:
                fvalue = float(res[0][1])
                # allcss[res[0][0]] = int(fvalue) if fvalue > 0.0 else -int(fvalue)
                allcss[res[0][0]] = fvalue

    if DEBUG:
        with codecs.open(os.path.join(tmpdir, 'lz.css.parse'), 'wb', 'utf8') as f:
            for k, v in allcss.items():
                f.write('{}\t{}\n'.format(k, v))
    return allcss


def dealDivC(hhx, precurdiv, lzcss):
    newdiv = []

    divcss = ''.join(hhx.xpath('./@class').extract()).strip()

    if precurdiv.startswith('<div class="c '):
        cx = lzcss[xpat.findall(divcss)[0]]
        cy = lzcss[ypat.findall(divcss)[0]]
        # ch = lzcss[hpat.findall(divcss)[0]]

        start = cy

        for hhhx in hhx.xpath('./div'):
            tmpdiv = ''.join(hhhx.xpath('.//text()').extract()).strip()
            tmpcss = hhhx.xpath('./@class').extract()[0]

            tmpcx = lzcss[xpat.findall(tmpcss)[0]]

            # print(tmpcx)
            tmpcy = lzcss[ypat.findall(tmpcss)[0]]

            newdiv.append((start + tmpcy, '<wr class="x{} y{}">{}</wr>'.format(cx + tmpcx, start + tmpcy, tmpdiv)))

    else:
        precurdiv = ''.join(hhx.xpath('.//text()').extract()).strip()
        cx = lzcss[xpat.findall(divcss)[0]]
        cy = lzcss[ypat.findall(divcss)[0]]
        newdiv.append((cy, '<wr class="x{} y{}">{}</wr>'.format(cx, cy, precurdiv)))

    return newdiv


def formatHtmlNotTable(tmphtml):
    hxs = Selector(text=tmphtml)

    tmp = {}

    xs = []
    ys = []

    hxs = hxs.xpath('/html/body')

    for e in hxs.xpath('./wr'):
        value = e.xpath('.//text()').extract()

        value = ''.join(value).strip()

        if value:
            wrcss = e.xpath('./@class').extract()[0]
            x = float(xfpat.findall(wrcss)[0])
            y = float(yfpat.findall(wrcss)[0])

            xs.append(x)
            ys.append(y)

            tmp[(y, x)] = value

    x_len = len(set(xs))
    y_len = len(set(ys))

    sorted_xs = sorted(set(xs), key=lambda x: x)
    sorted_ys = sorted(set(ys), key=lambda x: x, reverse=True)

    id2x = {}
    x2id = {}
    # map
    for idx, xx in enumerate(sorted_xs):
        id2x[idx] = xx
        x2id[xx] = idx

    id2y = {}
    y2id = {}
    # map
    for idx, yy in enumerate(sorted_ys):
        id2y[idx] = yy
        y2id[yy] = idx

    myarray = np.zeros((y_len, x_len))

    for kk in tmp:
        myarray[y2id[kk[0]]][x2id[kk[1]]] = 1

    buf = []

    for idy, r in enumerate(myarray):
        tmpbuf = []
        for idx, c in enumerate(r):
            if c == 1.0:
                tmpbuf.append(tmp[(id2y[idy], id2x[idx])])
        tmpbufvalue = ' '.join(tmpbuf)

        # 去掉pdf的页码标记
        if not just_digit_pat.match(tmpbufvalue):
            buf.append('<div>')
            buf.append(tmpbufvalue)
            buf.append('</div>')

    return ''.join(buf)


def formatHtml(tmphtml, extra_info):
    hxs = Selector(text=tmphtml)

    tmp = {}

    xs = []
    ys = []

    hxs = hxs.xpath('/html/body')

    for e in hxs.xpath('./wr'):
        value = e.xpath('.//text()').extract()
        value = ''.join(value).strip()

        if value:
            wrcss = e.xpath('./@class').extract()[0]
            x = float(xfpat.findall(wrcss)[0])
            y = float(yfpat.findall(wrcss)[0])

            xs.append(x)
            ys.append(y)

            tmp[(y, x)] = value

    x_len = len(set(xs))
    y_len = len(set(ys))

    sorted_xs = sorted(set(xs), key=lambda x: x)
    sorted_ys = sorted(set(ys), key=lambda x: x, reverse=True)

    id2x = {}
    x2id = {}
    # map
    for idx, xx in enumerate(sorted_xs):
        id2x[idx] = xx
        x2id[xx] = idx

    id2y = {}
    y2id = {}
    # map
    for idx, yy in enumerate(sorted_ys):
        id2y[idx] = yy
        y2id[yy] = idx

    myarray = np.zeros((y_len, x_len))

    for kk in tmp:
        myarray[y2id[kk[0]]][x2id[kk[1]]] = 1

    svgx = extra_info['rl'][0]
    svgy = extra_info['rl'][1]

    buf = ['<div><svg xmlns="http://www.w3.org/2000/svg" width="' + extra_info[
        'w'] + '" height="' + extra_info[
               'h'] + '" style="font-size:8px;" version="1.1">']
    buf.append('<rect width="' + extra_info[
        'w'] + '" height="' + extra_info[
                   'h'] + '" style="fill:rgb(255,255,255);stroke-width:1;stroke:rgb(0,0,0)"></rect>')
    myarray_list = myarray.tolist()
    for idy, r in enumerate(myarray_list):
        for idx, c in enumerate(r):
            if c == 1.0:
                affiney = float(svgy) - id2y[idy]
                affinex = id2x[idx] - float(svgx)
                buf.append(
                    '<text x =' + str(affinex) + ' dy=' + str(affiney) + ' >' + tmp[(id2y[idy], id2x[idx])] + '</text>')
    buf.append('</svg></div>')

    return ''.join(buf)


def getfinalhtml(tmpdir, lzhtmlparse, lzoutlineparse):
    buf = lzhtmlparse

    for k, v in lzoutlineparse.items():
        buf = k.sub(v, buf)

    if DEBUG:
        with codecs.open(tmpdir + '.html', 'wb', 'utf8') as f:
            f.write(buf)

    return buf


def create_new_html(tmpdir, lzcssparse, topic=None):
    lzhtml = []
    with codecs.open(os.path.join(tmpdir, 'lz.html'), 'rb', 'utf8') as f:
        for l in f.readlines():
            lzhtml.append(l.strip())
    lzhtml = ''.join(lzhtml)

    hxs = Selector(text=lzhtml)

    all_lz_html = []

    # 按页进行解析，因为position会重置
    for i, hx in enumerate(hxs.xpath('//div[contains(@id,"pf")]')):

        # print('page', i)
        new_lz_html = []

        notTableHtml = []

        img = hx.xpath('./div/img').extract()

        existTable = False
        newBoundRects = None
        img_class = None
        img_src = None

        # 得到table的y坐标范围
        tables_all_scale = []
        extra_tables_info = []

        if img:
            img_class = hx.xpath('./div/img/@class').extract()[0]
            img_src = hx.xpath('./div/img/@src').extract()[0]

            boundRects, h, w = extrTablePosition(os.path.join(tmpdir, img_src))
            if boundRects:
                new_x = lzcssparse[xpat.findall(img_class)[0]]
                new_y = lzcssparse[ypat.findall(img_class)[0]]
                new_w = lzcssparse[wpat.findall(img_class)[0]]
                new_h = lzcssparse[hpat.findall(img_class)[0]]

                # 缩放大小
                scale = h * 1.0 / new_h

                newBoundRects = combine(boundRects)

                # print(len(newBoundRects), newBoundRects)

                for newBoundRect in newBoundRects:
                    tables_all_scale.append((newBoundRect[0] / scale + new_x, (h - newBoundRect[1]) / scale + new_y,
                                             newBoundRect[2] / scale + new_x, (h - newBoundRect[3]) / scale + new_y))

                    tablex = newBoundRect[2] - newBoundRect[0]
                    tabley = newBoundRect[3] - newBoundRect[1]

                    extra_tables_info.append({'w': str(tablex / scale), 'h': str(tabley / scale), 'rl': (
                        str(newBoundRect[0] / scale + new_x), str((h - newBoundRect[1]) / scale + new_y))})
                existTable = True

        tables = defaultdict(list)

        for hhx in hx.xpath('./div/div'):
            precurdiv = hhx.extract()
            # print(precurdiv)

            # print('curdiv', curdiv)
            # print('divcss',divcss)
            for dd in dealDivC(hhx, precurdiv, lzcssparse):
                div_y = dd[0]
                curdiv = dd[1]

                # print(div_y, curdiv)

                if existTable:
                    divInTable = False
                    for j, table_scale in enumerate(tables_all_scale):
                        if div_y > table_scale[3] and div_y < table_scale[1]:
                            tables[j].append(curdiv)
                            divInTable = True
                            # print('find table!!', j)
                            break

                    if not divInTable:

                        # print('=', tables)
                        if tables:
                            if notTableHtml:
                                other_div = formatHtmlNotTable(''.join(notTableHtml))
                                if other_div:
                                    new_lz_html.append(other_div)
                                notTableHtml = []

                            for k, v in tables.items():
                                # print('<div class="table-' + str(i) + '-' + str(k) + '">' + ''.join(v) + '</div>')
                                new_lz_html.append(
                                    '<lz data-tab="table-' + str(i) + '-' + str(k) + '">' + formatHtml(''.join(v),
                                                                                                    extra_tables_info[
                                                                                                        k]) + '</lz>')

                            tables.clear()

                        # print('-', curdiv)
                        # new_lz_html.append(curdiv)
                        notTableHtml.append(curdiv)
                else:
                    # new_lz_html.append(curdiv)
                    notTableHtml.append(curdiv)

        if notTableHtml:
            other_div = formatHtmlNotTable(''.join(notTableHtml))
            if other_div:
                new_lz_html.append(other_div)
            notTableHtml = []

        # 考虑表格在末尾的情况
        if tables:
            for k, v in tables.items():
                # print('<div class="table-' + str(i) + '-' + str(k) + '">' + ''.join(v) + '</div>')
                new_lz_html.append(
                    '<lz data-tab="table-' + str(i) + '-' + str(k) + '">' + formatHtml(''.join(v), extra_tables_info[
                        k]) + '</lz>')

            tables.clear()

        if not new_lz_html:
            raise RuntimeError('pdf:{}可能是图片'.format(tmpdir))

        if all_lz_html and new_lz_html[0].startswith('<lz data-tab="table-') and all_lz_html[-1].endswith('</lz>'):
            all_lz_html[-1] = all_lz_html[-1][:-5]
            new_lz_html[0] = tableheadpat.sub('', new_lz_html[0])
            print('合并单元格!!{}-{}'.format(i - 1, i))
        all_lz_html.append(''.join(new_lz_html))
    return ''.join(all_lz_html)


def extractColumns(tmpdir, lzhtmlparse):
    buf = lzhtmlparse
    level1_tags_pat = re.compile('<div>(第[一二三四五六七八九十]+节.+?)</div>')
    level2_tags_pat = re.compile('<div>([一二三四五六七八九十]+、.+?)</div>')

    tags_pats = [level1_tags_pat, level2_tags_pat]

    findRes = {}

    for tags_pat in tags_pats:
        for idx, res in enumerate(tags_pat.findall(buf)):
            findRes[res] = '<div class="Section">' + res + '</div>'

    for k, v in findRes.items():
        buf = buf.replace('<div>' + k + '</div>', v)

    if DEBUG:
        with codecs.open(tmpdir + '.html', 'wb', 'utf8') as f:
            f.write(buf)

    print(buf)

    return buf


def lz_pdf2html(filepath, topic=None):
    logger.info('=' * 30)
    logger.info('解析文件开始:{},topic:{}'.format(filepath, topic))

    try:
        tmpdir = os.path.join(PREFIX, filepath.split('/')[-1].split('.')[0])
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
        os.makedirs(tmpdir)

        logger.info('开始粗分析pdf转html:{},topic:{}'.format(filepath, topic))
        t = time.time()
        ret = getPdf2htmlex(filepath, tmpdir)
        if ret != 0:
            raise RuntimeError('pdf2htmlEx分析pdf转html失败！！')
        logger.info('完成粗分析pdf转html:{}/{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        logger.info('开始提取大纲:{}/{}'.format(filepath, topic))
        t = time.time()
        lzoutlineparse = getOutline(tmpdir)
        logger.info('完成提取大纲:{}/{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        logger.info('开始提取样式:{}/{}'.format(filepath, topic))
        t = time.time()
        lzcssparse = getCss(tmpdir)
        logger.info('完成提取样式:{}/{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        logger.info('开始解析整体html:{}/{}'.format(filepath, topic))
        t = time.time()
        lzhtmlparse = create_new_html(tmpdir, lzcssparse)
        logger.info('完成开始解析整体html:{}/{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        # logger.info('合并最终html文件:{}/{}'.format(filepath, topic))
        # t = time.time()
        # finalhtml1 = getfinalhtml(tmpdir, lzhtmlparse, lzoutlineparse)
        # logger.info('完成最终html文件:{},topic:{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        logger.info('识别目录:{}/{}'.format(filepath, topic))
        t = time.time()
        finalhtml = extractColumns(tmpdir, lzhtmlparse)
        logger.info('识别目录文件:{},topic:{}=>耗时:{}'.format(filepath, topic, time.time() - t))

        if not DEBUG:
            shutil.rmtree(tmpdir)

        logger.info('正确解析完成:{}'.format(filepath))

        return finalhtml
    except Exception as e:
        if not DEBUG:
            shutil.rmtree(tmpdir)
        logging.error('错误解析完成:{},{}'.format(filepath, e))
        return None


if __name__ == '__main__':
    all_lz_html = lz_pdf2html('/home/sunchao/code/project/local-test/localtest/LzPdf2Html/demo/1202695002.PDF')
    # print(all_lz_html)

    # 扫描文件夹，
    # for root, _, filenames in os.walk('/myJob/liangzhi/myapps/juchaonianbao/mydownload'):
    #     for filename in filenames:
    #         filepath = os.path.join(root, filename)
    #         finalhtml = lz_pdf2html(filepath)
    #         if finalhtml:
    #             tmpdir = filepath.split('/')[-1].split('.')[0]
    #             with codecs.open(os.path.join(PREFIX, tmpdir + '.html'), 'wb', 'utf8') as f:
    #                 f.write(finalhtml)
