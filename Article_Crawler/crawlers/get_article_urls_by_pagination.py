#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: get_article_urls_by_pagination.py
# @Description: 文章链接爬取（用于通过页码拼接实现分页的网站）
# @Time: 2018/11/21 15:56
# @Author: ljz

import datetime
import hashlib

import pymysql
import requests
from lxml import etree

from utils import logger, mysql_pool, html_parser, judge_page_is_end


class Crawler:
    def __init__(self, page_name, page_url, page_pagination_url, start_pagination_number, page_is_end,
                 article_xpath, article_url_xpath, start_article_number, end_article_number, article_number_gap):
        """
        初始化爬虫对象
        :param page_name: 网页名称
        :param page_url: 网页url
        :param page_pagination_url: 网页url分页拼接部分
        :param start_pagination_number: 网页分页开始页码
        :param page_is_end: 判断网页分页是否结束的方法
        :param article_xpath: 文章在HTML代码中的标签的xpath路径
        :param article_url_xpath: 文章url在HTML代码中的标签的xpath路径
        :param start_article_number: 文章在HTML代码中的标签的开始编号
        :param end_article_number: 文章在HTML代码中的标签的结束编号
        :param article_number_gap: 编号间隔
        """
        self._page_name = page_name
        self._page_url = page_url
        self._page_pagination_url = page_pagination_url
        self._start_pagination_number = start_pagination_number
        self._page_is_end = page_is_end
        self._article_xpath = article_xpath
        self._article_url_xpath = article_url_xpath
        self._start_article_number = start_article_number
        self._end_article_number = end_article_number
        self._article_number_gap = article_number_gap
        self._mysql = mysql_pool.MyMysqlPool('dbMysql')
        self._crawl_flag = 0
        self._logger = logger.Logger('../log/{0}.log'.format(datetime.date.today()), page_name)
        self._html_parser = html_parser.HtmlParser()
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

    def parse_web_page(self, page_encoding='utf-8'):
        """
        解析网页
        :param page_encoding: 网页编码
        :return:
        """
        self._logger.add_log('info', '开始爬取 {0} 站点的数据'.format(self._page_name))
        self._create_table()
        running_flag = True
        page_number = 0
        while running_flag:
            page_number += 1

            if page_number < self._start_pagination_number:
                url = self._page_url.format('')
            else:
                url = self._page_url.format(self._page_pagination_url).format(str(page_number))

            if self._page_is_end == 'single page':
                if page_number > 1:
                    break
            elif self._page_is_end == '404':
                if judge_page_is_end.error_404(url):
                    break
            else:
                if judge_page_is_end.no_data(url, self._page_is_end):
                    break

            page_request = requests.get(url, headers=self._headers)
            page_request.encoding = page_encoding
            article_urls, contents = self._get_page_data(page_request.text, page_encoding)

            for index in range(len(article_urls)):
                if self._crawl_flag >= 3:
                    self._logger.add_log('info', '更新爬取结束')
                    running_flag = False
                    break
                self._insert_article_urls(article_urls[index], contents[index])
        self._logger.add_log('info', '{0} 站点数据爬取完毕'.format(self._page_name))

    def _get_page_data(self, page_source, page_encoding):
        """
        获取网页上的文章url及其HTML相关内容
        :param page_source: 网页数据
        :param page_encoding: 网页编码
        :return: 文章url及其HTML相关内容
        """
        article_urls = []
        contents = []
        index = self._start_article_number
        while index <= self._end_article_number:
            content = self._html_parser.parse_by_xpath(page_source, self._article_xpath.format(index), page_encoding)
            xpath_change = self._article_xpath + self._article_url_xpath
            article_url = self._html_parser.parse_by_xpath(page_source, xpath_change.format(index), page_encoding)
            if content and article_url:
                for i in range(len(content)):
                    contents.append(etree.tostring(content[i], encoding=page_encoding).decode(page_encoding))
                    article_urls.append(article_url[i])
            index += self._article_number_gap

        return article_urls, contents

    def _insert_article_urls(self, article_url, content):
        """
        向数据库插入文章url及其HTML相关内容
        :param article_url: 文章url
        :param content: HTML相关内容
        :return:
        """
        article_url_md5 = hashlib.md5(article_url.encode(encoding='UTF-8')).hexdigest()
        crawl_time = datetime.datetime.now()
        try:
            self._mysql.insert("""
            INSERT INTO page_list.`{0}` (url, url_md5, content, is_visited, crawl_time) VALUES 
            ('{1}', '{2}', '{3}', FALSE, '{4}')
            """.format(self._page_name, article_url, article_url_md5,
                       content.replace('\\', '\\\\').replace('\'', '\\\''), crawl_time))
        except pymysql.err.IntegrityError:
            self._crawl_flag += 1
            self._logger.add_log('warning', '插入失败，已有相同url（{0}）'.format(article_url))
        else:
            self._crawl_flag = 0

    def _create_table(self):
        """
        根据网页名称建立相应数据表
        :return:
        """
        sql = """
        CREATE TABLE IF NOT EXISTS page_list.`{0}`  (
          `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
          `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `url_md5` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `is_visited` tinyint(1) NOT NULL,
          `crawl_time` datetime(0) NOT NULL,
          PRIMARY KEY (`url`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
        """.format(self._page_name)
        self._mysql.create(sql)
