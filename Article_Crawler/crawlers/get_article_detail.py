#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: get_article_detail.py
# @Description: 文章详情爬取
# @Time: 2018-11-25 16:16
# @Author: ljz

import datetime
import hashlib

import pymysql
import requests
from lxml import etree

from utils import logger, mysql_pool, parse_page_body, html_parser


class Crawler:
    def __init__(self, page_name, page_url, title_xpath, content_xpath, detail_splice_flag, splice_base_url):
        """
        初始化爬虫对象
        :param page_name: 网页名称
        :param page_url: 网页url
        :param title_xpath: 文章标题的xpath路径
        :param content_xpath: 文章内容的xpath路径
        :param detail_splice_flag: 网页url是否需要拼接
        :param splice_base_url: 拼接的基础url
        """
        self._page_name = page_name
        self._page_url = page_url
        self._title_xpath = title_xpath
        self._content_xpath = content_xpath
        self._detail_splice_flag = detail_splice_flag
        self._splice_base_url = splice_base_url
        self._mysql = mysql_pool.MyMysqlPool('dbMysql')
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
        if self._detail_splice_flag == 'true':
            url = self._splice_base_url.format(self._page_url)
        else:
            url = self._page_url
        self._logger.add_log('info', '开始爬取文章（{0}）的内容'.format(url))
        self._create_table()
        try:
            page_request = requests.get(url, headers=self._headers)
            page_request.encoding = page_encoding
            try:
                article_title = self._html_parser.parse_by_xpath(page_request.text,
                                                                 self._title_xpath, page_encoding)[0]
            except IndexError:
                article_title = ''
            try:
                xpath_result = self._html_parser.parse_by_xpath(page_request.text, self._content_xpath, page_encoding)
                xpath_result_tostring = etree.tostring(xpath_result[0], encoding=page_encoding).decode(page_encoding)
                article_content, article_img = parse_page_body.execute_by_content(xpath_result_tostring)
            except IndexError:
                article_content = ''
                article_img = []
            self._insert_content_data(url, article_title, article_content)

            for img in article_img:
                self._insert_img_data(url, img)
        except Exception as e:
            self._logger.add_log('error', '文章（{0}）爬取失败，异常：{1}'.format(url, repr(e)))
        else:
            self._logger.add_log('info', '文章（{0}）爬取完毕'.format(url))

    def _insert_content_data(self, url, article_title, article_content):
        """
        向数据库插入文章信息
        :param url: 文章链接
        :param article_title: 文章标题
        :param article_content: 文章内容
        :return:
        """
        page_url_md5 = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()
        crawl_time = datetime.datetime.now()
        try:
            self._mysql.insert("""
            INSERT INTO page_detail.`{0}` (url, url_md5, title, content, crawl_time) VALUES 
            ('{1}', '{2}', '{3}', '{4}', '{5}')
            """.format(self._page_name, url, page_url_md5, article_title.replace('\\', '\\\\').replace('\'', '\\\''),
                       article_content.replace('\\', '\\\\').replace('\'', '\\\''), crawl_time))
        except pymysql.err.IntegrityError:
            self._logger.add_log('warning', '插入失败，已有相同url（{0}）'.format(url))
            self._mysql.update("""
            UPDATE page_list.`{0}` SET is_visited=TRUE WHERE url='{1}'
            """.format(self._page_name, self._page_url))
        except Exception as e:
            raise e
        else:
            self._mysql.update("""
            UPDATE page_list.`{0}` SET is_visited=TRUE WHERE url='{1}'
            """.format(self._page_name, self._page_url))

    def _insert_img_data(self, url, img):
        """
        向数据库插入文章中的图片链接
        :param url: 文章链接
        :param img: 文章中的图片链接
        :return:
        """
        try:
            self._mysql.insert("""
            INSERT INTO page_detail.img (url, img_url_md5, img_url) VALUES ('{0}', '{1}', '{2}')
            """.format(url, img[0], img[1]))
        except pymysql.err.IntegrityError:
            self._logger.add_log('warning', '插入失败，已有相同图片（{0}）'.format(img[1]))
        except Exception as e:
            raise e

    def _create_table(self):
        """
        根据网页名称建立相应数据表
        :return:
        """
        sql = """
        CREATE TABLE IF NOT EXISTS page_detail.`{0}`  (
          `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
          `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `url_md5` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
          `content` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
          `crawl_time` datetime(0) NOT NULL,
          PRIMARY KEY (`url`) USING BTREE
        ) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;
        """.format(self._page_name)
        self._mysql.create(sql)
