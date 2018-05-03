# -*- coding:UTF-8 -*-
#!/usr/bin/env python3

import pymysql
import time


def update_mysql():
    db = pymysql.connect('192.168.1.252', 'root', '123456', 'supermind_config')
    cursor = db.cursor()
    local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    sql = "UPDATE pipeline_config SET update_time='%s' WHERE name='local_guquanbiandong';" % local_time
    try:
       # 执行SQL语句
       cursor.execute(sql)
       # 提交到数据库执行
       db.commit()
    except:
       # 发生错误时回滚
       db.rollback()
    db.close()
