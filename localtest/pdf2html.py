# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import os
import shutil
import subprocess
import re

re_space = re.compile('\s+')
RESULT_PREFIX = 'myResultHtml'


########
# pdf2html预处理
########
def getPdf2htmlex(filepath, tmpdir):
    subprocess.call(
        "pdf2htmlEX --process-nontext 1 --embed-font 1 --optimize-text 1 --printing 0 --embed-javascript 0 --embed-external-font 0 --embed-outline 0 --process-outline 0 --space-as-offset 1 --dest-dir " + tmpdir + " " + filepath + " lz.html",
        shell=True)


def getPdf2html(path):
    for root, _, filenames in os.walk(path):

        for filename in filenames:
            try:
                filepath = os.path.join(root, filename)
                filepath = re_space.sub('', filepath)
                print('开始处理：' + filepath)

                tmpdir = filepath.split('/')[-1].split('.')[0]
                tmpdir = os.path.join(RESULT_PREFIX, tmpdir)
                if os.path.exists(tmpdir):
                    shutil.rmtree(tmpdir)
                os.makedirs(tmpdir)

                getPdf2htmlex(filepath, tmpdir)
            except Exception as e:
                print('{}:{}'.format(e, filepath))
                continue


if __name__ == '__main__':
    pdf2html('/home/sunchao/code/project/local-test/localtest/download')

