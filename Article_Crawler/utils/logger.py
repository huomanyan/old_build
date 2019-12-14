#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: logger.py
# @Description: 日志配置
# @Time: 2018/11/26 10:39
# @Author: ljz

import logging


class Logger:
    """
    日志类
    """
    def __init__(self, logger_path, module_name):
        """
        初始化日志
        :param logger_path: 日志文件路径
        :param module_name: 模块名称
        """
        self._logger = logging.getLogger(module_name)
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(logging.INFO)
        self._console_handler.setFormatter(formatter)
        self._file_handler = logging.FileHandler(logger_path, encoding='utf-8')
        self._file_handler.setLevel(logging.INFO)
        self._file_handler.setFormatter(formatter)

    def add_log(self, level, content=''):
        """
        添加日志内容
        :param level: 日志级别
        :param content: 日志内容
        :return: 
        """
        self._logger.addHandler(self._console_handler)
        self._logger.addHandler(self._file_handler)
        if level == 'debug':
            self._logger.debug(content)
        elif level == 'info':
            self._logger.info(content)
        elif level == 'warning':
            self._logger.warning(content)
        elif level == 'error':
            self._logger.error(content)
        elif level == 'critical':
            self._logger.critical(content)
        self._logger.removeHandler(self._console_handler)
        self._logger.removeHandler(self._file_handler)
