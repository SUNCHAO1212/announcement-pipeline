# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pymysql
import time


def get_mysql_queues():
    db = pymysql.connect('192.168.1.252', 'root', '123456', 'supermind_config')
    cursor = db.cursor()
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql1 = "UPDATE pipeline_config SET update_time='%s' WHERE name='local_guquanbiandong';" % local_time
    try:
        # 执行SQL语句
        cursor.execute(sql1)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    queues_dict = {}
    sql2 = "SELECT * FROM pipeline_config WHERE name = 'local_guquanbiandong'"
    try:
        # 执行SQL语句
        cursor.execute(sql2)
        result = cursor.fetchall()
        for row in result:
            queues_dict['exchange'] = (row[3])
            queues_dict['read'] = (row[4])
            queues_dict['write'] = (row[5])
    except:
        db.rollback()
    db.close()
    return queues_dict


# print(get_mysql_queues())
