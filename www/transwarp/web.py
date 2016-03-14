#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
这是一个简单的， 轻量级的， WSGI兼容(Web Server Gateway Interface)的web 框架
WSGI概要：
    工作方式： WSGI server -----> WSGI 处理函数
    作用：将HTTP原始的请求、解析、响应 这些交给WSGI server 完成，
          让我们专心用Python编写Web业务，也就是 WSGI 处理函数
          所以WSGI 是HTTP的一种高级封装。
    例子：
        wsgi 处理函数
            def application(environ, start_response):
                method = environ['REQUEST_METHOD']
                path = environ['PATH_INFO']
                if method=='GET' and path=='/':
                return handle_home(environ, start_response)
                if method=='POST' and path='/signin':
                return handle_signin(environ, start_response)
        wsgi server
            def run(self, port=9000, host='127.0.0.1'):
                from wsgiref.simple_server import make_server
                server = make_server(host, port, application)
                server.serve_forever()

设计web框架的原因：
    1. WSGI提供的接口虽然比HTTP接口高级了不少，但和Web App的处理逻辑比，还是比较低级，
       我们需要在WSGI接口之上能进一步抽象，让我们专注于用一个函数处理一个URL，
       至于URL到函数的映射，就交给Web框架来做。
设计web框架接口：
    1. URL路由： 用于URL 到 处理函数的映射
    2. URL拦截： 用于根据URL做权限检测
    3. 视图： 用于HTML页面生成
    4. 数据模型： 用于抽取数据（见models模块）
    5. 事物数据：request数据和response数据的封装（thread local）
"""

import types,os,re,cgi,sys,time,datetime,functools,threading,logging
from db import Dict

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#################################################################
# 实现事物数据接口, 实现request 数据和response数据的存储,
# 是一个全局ThreadLocal对象
#################################################################
ctx = threading.local()

_RE_RESPONSE_STATUS = re.compile(r'^\d\d\d(\ [\w\ ]+)?$') #^表示行的开头，^\d表示必须以数字开头,$表示行的结束
_HEADER_X_POWERED_BY = ('X-Powered-By','transwarp/1.0')

#  用于时区转换
_TIMEDELTA_ZERO = datetime.timedelta(0)
_RE_TZ = re.compile('^([\+\-])([0-9]{1,2})\:([0-9]{1,2})$')

class UTC(datetime.tzinfo):
    """
    tzinfo 是一个基类，用于给datetime对象分配一个时区
    使用方式是 把这个子类对象传递给datetime.tzinfo属性
    传递方法有2种：
        １.　初始化的时候传入
            datetime(2009,2,17,19,10,2,tzinfo=tz0)
        ２.　使用datetime对象的 replace方法传入，从新生成一个datetime对象
            datetime.replace(tzinfo= tz0）
    >>> tz0 = UTC('+00:00')
    >>> tz0.tzname(None)
    'UTC+00:00'
    >>> tz8 = UTC('+8:00')
    >>> tz8.tzname(None)
    'UTC+8:00'
    >>> tz7 = UTC('+7:30')
    >>> tz7.tzname(None)
    'UTC+7:30'
    >>> tz5 = UTC('-05:30')
    >>> tz5.tzname(None)
    'UTC-05:30'
    >>> from datetime import datetime
    >>> u = datetime.utcnow().replace(tzinfo=tz0)
    >>> l1 = u.astimezone(tz8)
    >>> l2 = u.replace(tzinfo=tz8)
    >>> d1 = u - l1
    >>> d2 = u - l2
    >>> d1.seconds
    0
    >>> d2.seconds
    28800
    """
    def __init__(self,utc):
        utc = str(utc.strip().upper()) #删除开头结尾处的字符，为空时，默认删除空白符（包括'\n', '\r',  '\t',  ' ')
        mt = _RE_TZ.match(utc)
        if mt:
            minus = mt.group(1) == '-'
            h = int(mt.group(2))
            m = int(mt.group(3))
            if minus:
                h,m = (-h),(-m)
            self._utcoffset = datetime.timedelta(hours=h,minutes=m)
            self._tzname = 'UTC%s'%utc
        else:
            raise ValueError('bad utc time zone')


