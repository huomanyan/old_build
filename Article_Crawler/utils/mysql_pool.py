#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: mysql_pool.py
# @Description: MySQL操作封装
# @Time: 2018/11/21 14:43
# @Author: ljz

import configparser
import datetime
import os
import pymysql
from DBUtils.PooledDB import PooledDB

from utils import logger


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


class MyMysqlPool(BaseMysqlPool):

    def __init__(self, conf_name=None):
        self.conf = Config().get_content(conf_name)
        super(MyMysqlPool, self).__init__(**self.conf)
        self.__pool = PooledDB(creator=pymysql,
                               maxconnections=0,
                               mincached=1,
                               maxcached=0,
                               blocking=True,
                               maxusage=None,
                               host=self.db_host,
                               port=self.db_port,
                               user=self.user,
                               passwd=self.password,
                               db=self.db,
                               charset="utf8mb4")
        self._logger = logger.Logger('../log/{0}.log'.format(datetime.date.today()), 'mysql')

    def _execute(self, sql, param=None):
        connect = self.__pool.connection()
        cursor = connect.cursor()
        try:
            cursor.execute(sql)
            connect.commit()
            if param == 'select_one':
                result = cursor.fetchone()
            elif param == 'select_all':
                result = cursor.fetchall()
            else:
                result = None
            cursor.close()
            connect.close()
            return result
        except pymysql.err.IntegrityError:
            raise pymysql.err.IntegrityError
        except Exception as e:
            self._logger.add_log('error', '数据库 {} 错误, sql: {}'.format(e, sql))
            connect.rollback()
            cursor.close()
            connect.close()
            raise e

    def insert(self, sql):
        self._execute(sql)

    def update(self, sql):
        self._execute(sql)

    def create(self, sql):
        self._execute(sql)

    def select_one(self, sql):
        return self._execute(sql, 'select_one')

    def select_all(self, sql):
        return self._execute(sql, 'select_all')
