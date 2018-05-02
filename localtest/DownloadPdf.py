# -*- coding: utf-8 -*-
# !/usr/bin/env python

from __future__ import absolute_import, unicode_literals, print_function

import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import urllib
import codecs
import json
import re

error = codecs.open('files/downloadError.txt', 'wb', 'utf8')
PREFIX = 'download/'


def getFile(url, filename):
    try:
        u = urllib.request.urlopen(url, timeout=5)
        f = open(PREFIX + filename + '.pdf', 'wb')

        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            f.write(buffer)
        f.close()
        print("Sucessful to download" + " " + str(i))

    except Exception as e:
        print(e)
        error.write(url + ' ' + filename + '\n')


pattern = re.compile('<.+?>')
re_space = re.compile('\s+')


def clean_title(string):
    string = re.sub(pattern, '', string)
    string = re.sub(re_space, '', string)
    return string


if __name__ == '__main__':

    with open('files/urls_增持.txt') as f:
        i = 1
        for line in f:
            data_dict = json.loads(line)
            title = clean_title(data_dict['title'])
            url = data_dict['url']
            print(url)
            print(title)
            # getFile(url, title)
            i += 1
            if i > 10:
                break
