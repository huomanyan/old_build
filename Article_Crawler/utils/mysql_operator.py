#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: mysql_operator.py
# @Description: MySQL操作封装
# @Time: 2018/11/21 14:43
# @Author: ljz

import configparser
import os
import pymysql
from DBUtils.PooledDB import PooledDB


class Config(object):

    def __init__(self, config_filename="../config/DBUtils_MySQL.cnf"):
        file_path = os.path.join(os.path.dirname(__file__), config_filename)
        self.cf = configparser.ConfigParser()
        self.cf.read(file_path)

    def get_sections(self):
        return self.cf.sections()

    def get_options(self, section):
        return self.cf.options(section)

    def get_content(self, section):
        result = {}
        for option in self.get_options(section):
            value = self.cf.get(section, option)
            result[option] = int(value) if value.isdigit() else value
        return result


class BaseMysqlPool(object):
    def __init__(self, host, port, user, password, db_name=None):
        self.db_host = host
        self.db_port = int(port)
        self.user = user
        self.password = str(password)
        self.db = db_name
        self.conn = None
        self.cursor = None


class MyMysqlPool(BaseMysqlPool):
    """
    MySQL数据库对象
    """
    __pool = None

    def __init__(self, conf_name=None):
        self.conf = Config().get_content(conf_name)
        super(MyMysqlPool, self).__init__(**self.conf)
        self._connect = self._get_connection()
        self._cursor = self._connect.cursor()

    def _get_connection(self):
        """
        获取pymysql.connect
        :return: pymysql.connect
        """
        if MyMysqlPool.__pool is None:
            self.__pool = PooledDB(creator=pymysql,
                                   mincached=1,
                                   maxcached=20,
                                   host=self.db_host,
                                   port=self.db_port,
                                   user=self.user,
                                   passwd=self.password,
                                   db=self.db,
                                   autocommit=1,
                                   charset="utf8mb4")
        return self.__pool.connection()

    def get_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = None
        return result

    def get_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def get_many(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insert_many(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def _query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self._query(sql, param)

    def insert(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self._query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: sql语句
        @param param: sql语句参数
        @return: count 受影响的行数
        """
        return self._query(sql, param)

    def create(self, sql, param=None):
        """
        @summary: 新建操作
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self._query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._connect.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._connect.commit()
        else:
            self._connect.rollback()

    def dispose(self, is_end=1):
        """
        @summary: 释放连接池资源
        """
        if is_end == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._connect.close()

    def is_connection(self):
        """
        判断数据库是否连接
        :return: 数据库是否连接
        """
        try:
            self._connect.ping()
            return True
        except Exception:
            return False


if __name__ == '__main__':
    mysql = MyMysqlPool("dbMysql")
    a = mysql.is_connection()
    print(a)
    mysql.dispose()
    b = mysql.is_connection()
    print(b)
    mysql = MyMysqlPool("dbMysql")
    mysql.dispose()
