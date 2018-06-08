# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import re
import os
import codecs

from urllib.request import urlopen
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
from io import open

def rename():
    for root, _, files in os.walk('股权质押'):
        for filename in files:

            new_filename = re.sub('\[', '_', filename)
            new_filename = re.sub(']', '_', new_filename)
            new_filename = re.sub(':', '：', new_filename)
            new_filename = re.sub('：', '_', new_filename)

            new_filename = re.sub('_+', '_', new_filename)

            print(filename, new_filename)

            os.rename(os.path.join(root, filename), os.path.join(root, new_filename))



def readPDF(pdfFile):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)

    process_pdf(rsrcmgr, device, pdfFile)
    device.close()

    content = retstr.getvalue()
    retstr.close()
    return content


if __name__ == '__main__':
    try:
        # fp = open(os.path.join('股权质押', '1205028310_临时公告_大洋教育_股权解除质押公告.PDF'), 'rb')
        fp = open(os.path.join('股权质押', '1204183395_临时公告_德御坊_股权质押及解除股权质押公告.PDF'), 'rb')
        outputString = readPDF(fp)
        print(outputString)
    except Exception as e:
        print(e)
    else:
        # 处理
        print('pass')
        pass
    finally:
        fp.close()