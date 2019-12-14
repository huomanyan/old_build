#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: controller.py
# @Description: 爬虫控制器
# @Time: 2018/11/26 19:24
# @Author: ljz

import datetime
import time
from configparser import ConfigParser

from crawlers import crawl_template
from utils import mysql_pool

mysql = mysql_pool.MyMysqlPool('dbMysql')


def start_crawler():
    for i in web_sites:
        if config_parser.get(i, 'mode') == 'pagination':
            param = {'page_name': config_parser.get(i, 'page_name'),
                     'page_url': config_parser.get(i, 'page_url'),
                     'page_pagination_url': config_parser.get(i, 'page_pagination_url'),
                     'start_pagination_number': config_parser.getint(i, 'start_pagination_number'),
                     'page_is_end': config_parser.get(i, 'page_is_end'),
                     'article_xpath': config_parser.get(i, 'article_xpath'),
                     'article_url_xpath': config_parser.get(i, 'article_url_xpath'),
                     'start_article_number': config_parser.getint(i, 'start_article_number'),
                     'end_article_number': config_parser.getint(i, 'end_article_number'),
                     'article_number_gap': config_parser.getint(i, 'article_number_gap')}
            crawl_template.template_get_article_urls_by_pagination(param)
        elif config_parser.get(i, 'mode') == 'dynamic loading':
            param = {'page_name': config_parser.get(i, 'page_name'),
                     'page_url': config_parser.get(i, 'page_url'),
                     'request_method': config_parser.get(i, 'request_method'),
                     'request_param': config_parser.get(i, 'request_param'),
                     'page_is_end': config_parser.get(i, 'page_is_end'),
                     'article_xpath': config_parser.get(i, 'article_xpath'),
                     'article_url_xpath': config_parser.get(i, 'article_url_xpath'),
                     'start_article_number': config_parser.getint(i, 'start_article_number'),
                     'end_article_number': config_parser.getint(i, 'end_article_number'),
                     'article_number_gap': config_parser.getint(i, 'article_number_gap')}
            crawl_template.template_get_article_urls_by_dynamic_loading(param)

        param = {'page_name': config_parser.get(i, 'page_name'),
                 'title_xpath': config_parser.get(i, 'title_xpath'),
                 'content_xpath': config_parser.get(i, 'content_xpath'),
                 'detail_splice_flag': config_parser.get(i, 'detail_splice_flag'),
                 'splice_base_url': config_parser.get(i, 'splice_base_url')}
        article_urls = mysql.select_all("""
        SELECT url FROM page_list.`{0}` WHERE is_visited=FALSE
        """.format(i))
        if article_urls:
            for j in article_urls:
                crawl_template.template_get_article_detail(param, j[0])
        update_page_info(config_parser.get(i, 'page_name'))


def update_page_info(page_name):
    mysql.update("""
    insert into page_list.page_set(name, update_time) values ('{0}', '{1}')
    on duplicate key update update_time='{1}'
    """.format(page_name, datetime.datetime.now()))


config_parser = ConfigParser()
config_parser.read('../config/web_sites.ini', encoding='utf-8')
web_sites = config_parser.sections()
while True:
    start_crawler()
    time.sleep(1800)
