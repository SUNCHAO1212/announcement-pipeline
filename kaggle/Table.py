# -*- coding:UTF-8 -*-
#!/usr/bin/env python3


import re
import copy


space = re.compile('\s')


def clean_sent(sent):
    sent = space.sub('', sent.strip())
    return sent


class Table:
    def __init__(self, html_table):
        self.html = html_table
        self.len_row, self.len_col = self.table_size()
        self.array = self.save_array()
        self.value_start = 0
        self.dict = self.get_key_value()

    def table_size(self):
        trs = self.html.tbody.find_all('tr')
        len_row = len(trs)
        tr = trs[0]
        tds = tr.find_all('td')
        len_col = len(tds)
        for i_td, td in enumerate(tds):
            if td.attrs and 'colspan' in td.attrs:
                len_col += int(td.attrs['colspan']) - 1
        return len_row, len_col

    def save_array(self):
        array = []
        for i in range(self.len_row):
            array.append(copy.deepcopy([None]*self.len_col))
        trs = self.html.tbody.find_all('tr')
        for i_tr, tr in enumerate(trs):
            tds = tr.find_all('td')
            for i_td, td in enumerate(tds):
                if td.attrs:
                    for key in td.attrs:
                        if key == 'rowspan':
                            for i in range(int(td.attrs[key])):
                                for j in range(i_td, self.len_col):
                                    if array[i_tr + i][j] is None:
                                        array[i_tr + i][j] = clean_sent(td.text)
                                        break
                                    else:
                                        pass
                        elif key == 'colspan':
                            for i in range(int(td.attrs[key])):
                                for j in range(i_td + i, self.len_col):
                                    if array[i_tr][j] is None:
                                        array[i_tr][j] = clean_sent(td.text)
                                        break
                                    else:
                                        pass
                        else:
                            print("Not span key.The key is: {}".format(key))
                else:
                    for j in range(i_td, self.len_col):
                        if array[i_tr][j] is None:
                            array[i_tr][j] = clean_sent(td.text)
                            break
                        else:
                            pass
        return array

    def show_array(self):
        for row in self.array:
            for col in row:
                if col:
                    print(col, end='\t')
                else:
                    print('[void]', end='\t')
            print('')

    def show_table(self):
        trs = self.html.tbody.find_all('tr')
        for i_tr, tr in enumerate(trs):
            print("<tr[{}]>".format(i_tr))
            tds = tr.find_all('td')
            for i_td, td in enumerate(tds):
                print("<td[{}]>{}\t".format(i_td, re.sub('\s', '', td.text.strip())), end='\t')
            print('')

    def get_key_value(self):
        keys = copy.deepcopy(self.array[0])
        for index in range(self.len_row):
            keys_set = set(keys)
            if len(keys_set) == self.len_col:
                self.value_start = index + 1
                break
                # return keys
            else:
                for i in range(self.len_col):
                    if keys[i] != self.array[index+1][i]:
                        keys[i] += '_'+self.array[index+1][i]
        temp_dict = {}
        for i, key in enumerate(keys):
            temp_dict[key] = []
            for row in range(self.value_start, self.len_row):
                temp_dict[key].append(self.array[row][i])
        return temp_dict
