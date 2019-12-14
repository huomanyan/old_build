#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: crawl_template.py
# @Description: 爬虫调用模板
# @Time: 2018/11/30 8:56
# @Author: ljz

from crawlers import get_article_urls_by_pagination, get_article_urls_by_dynamic_loading, get_article_detail


def template_get_article_urls_by_pagination(param, page_encoding='utf-8'):
    page = get_article_urls_by_pagination.Crawler(param['page_name'],
                                                  param['page_url'],
                                                  param['page_pagination_url'],
                                                  param['start_pagination_number'],
                                                  param['page_is_end'],
                                                  param['article_xpath'],
                                                  param['article_url_xpath'],
                                                  param['start_article_number'],
                                                  param['end_article_number'],
                                                  param['article_number_gap'])
    page.parse_web_page(page_encoding)
    del page


def template_get_article_urls_by_dynamic_loading(param, page_encoding='utf-8'):
    page = get_article_urls_by_dynamic_loading.Crawler(param['page_name'],
                                                       param['page_url'],
                                                       param['request_method'],
                                                       param['request_param'],
                                                       param['page_is_end'],
                                                       param['article_xpath'],
                                                       param['article_url_xpath'],
                                                       param['start_article_number'],
                                                       param['end_article_number'],
                                                       param['article_number_gap'])
    page.parse_web_page(page_encoding)
    del page


def template_get_article_detail(param, page_url, page_encoding='utf-8'):
    page = get_article_detail.Crawler(param['page_name'],
                                      page_url,
                                      param['title_xpath'],
                                      param['content_xpath'],
                                      param['detail_splice_flag'],
                                      param['splice_base_url'])
    page.parse_web_page(page_encoding)
    del page
