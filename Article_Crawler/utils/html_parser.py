#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: html_parser.py
# @Description: HTML解析器
# @Time: 2018/11/26 15:44
# @Author: ljz

import datetime
import json
import re

from lxml import etree

from utils import logger


class HtmlParser(object):
    """
    解析: re、xpath、json
    """
    def __init__(self):
        self._logger = logger.Logger('../log/{0}.log'.format(datetime.date.today()), "parse")

    def parse_by_json(self, page_source):
        """
        解析网页中的json数据
        :param page_source: 网页数据
        :return: 解析结果
        """
        try:
            data = json.loads(page_source)
        except:
            self._logger.add_log('error', 'json解析失败')
        else:
            return data

    def parse_by_xpath(self, page_source, page_xpath, page_encoding):
        """
        通过xpath解析网页
        :param page_source: 网页数据
        :param page_xpath: xpath路径
        :param page_encoding: 网页编码
        :return: 解析结果
        """
        try:
            page = etree.HTML(page_source, parser=etree.HTMLParser(encoding=page_encoding))
        except:
            self._logger.add_log('error', 'xpath解析失败')
        else:
            return page.xpath(page_xpath)

    def get_data_by_re(self, page_source, pattern, flags=re.DOTALL):
        """
        通过正则表达式解析网页
        :param page_source: 网页数据
        :param pattern: 正则表达式
        :param flags: 正则表达式参数
        :return: 解析结果
        """
        try:
            data = re.findall(pattern, page_source, flags=flags)
        except:
            self._logger.add_log('error', '正则解析失败')
        else:
            return data
