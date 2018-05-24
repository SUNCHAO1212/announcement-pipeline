# -*- coding:UTF-8 -*-
# !/usr/bin/env python3


import re

from bs4 import BeautifulSoup

from kaggle.Table import Table


def get_tables(html):
    bs = BeautifulSoup(html, 'lxml')
    tables = bs.find_all('table')
    for i_table, table in enumerate(tables):
        # print(table.prettify())
        table_info = Table(table)
        table_info.show_array()
        print(table_info.dict)
        print('')

    return False


def main():

    with open('data/31346.html') as f:
        html = f.read()
        tables = get_tables(html)


if __name__ == '__main__':
    main()