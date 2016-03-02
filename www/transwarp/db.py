#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设计db模块的原因：
  1. 更简单的操作数据库
      一次数据访问：   数据库连接 => 游标对象 => 执行SQL => 处理异常 => 清理资源。
      db模块对这些过程进行封装，使得用户仅需关注SQL执行。
  2. 数据安全
      用户请求以多线程处理时，为了避免多线程下的数据共享引起的数据混乱，
      需要将数据连接以ThreadLocal对象传入。
设计db接口：
  1.设计原则：
      根据上层调用者设计简单易用的API接口
  2. 调用接口
      1. 初始化数据库连接信息
          create_engine封装了如下功能:
              1. 为数据库连接 准备需要的配置信息
              2. 创建数据库连接(由生成的全局对象engine的 connect方法提供)
          from transwarp import db
          db.create_engine(user='root',
                           password='password',
                           database='test',
                           host='127.0.0.1',
                           port=3306)
      2. 执行SQL DML
          select 函数封装了如下功能:
              1.支持一个数据库连接里执行多个SQL语句
              2.支持链接的自动获取和释放
          使用样例:
              users = db.select('select * from user')
              # users =>
              # [
              #     { "id": 1, "name": "Michael"},
              #     { "id": 2, "name": "Bob"},
              #     { "id": 3, "name": "Adam"}
              # ]
      3. 支持事物
      transaction 函数封装了如下功能:
             1. 事务也可以嵌套，内层事务会自动合并到外层事务中，这种事务模型足够满足99%的需求
"""

import time,uuid,functools,threading,logging

def create_engine(user,password,database,host='127.0.0.1',port=3306,**kw):
    """
    db模型的核心函数，用于连接数据库, 生成全局对象engine，
    engine对象持有数据库连接
    """
    import MySQLdb
    global engine
    if engine is not None:
        raise MySQLdb.DatabaseError('Engine is already initialized.')
    params = dict(user=user,password=password,database=database,host=host,port=port)
    defaults = dict(use_unicode=True,charset='utf-8',collation='utf8_general_ci',autocommit=False,unix_socket='/opt/lampp/var/mysql/mysql.sock')
    for k,v in defaults.iteritems():
        params[k] = kw.pop(k,v)
    params.update(kw)
    params['buffered'] = True
    engine = _Engine(lambda:MySQLdb.connect(**params))
    # test connection...
    logging.info('Init mysql engine <%s> ok.'%hex(id(engine)))

# 数据库引擎对象:
class _Engine(object):
    """
    数据库引擎对象
    用于保存 db模块的核心函数：create_engine 创建出来的数据库连接
    """
    def __init__(self,connect):
        self._connect = connect
    def connect(self):
        return self._connect()

