#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: judge_page_is_end.py
# @Description: 判断网页是否还有数据
# @Time: 2018/11/22 9:46
# @Author: ljz

import requests
from lxml import etree


def error_404(page_url, method='get', param=None):
    """
    判断模板（404错误）
    :param page_url: 网页url
    :param method: 网页请求方法
    :param param: 网页参数
    :return: 网页是否还有数据
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
    if method == 'get':
        return requests.get(page_url, params=param, headers=headers).status_code == 404
    else:
        return requests.post(page_url, data=param, headers=headers).status_code == 404


def no_data(page_url, xpath, method='get', param=None):
    """
    判断模板（没有指定数据）
    :param page_url: 网页url
    :param xpath: 判断网页是否还有数据的xpath
    :param method: 网页请求方法
    :param param: 网页参数
    :return: 网页是否还有数据
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
    if method == 'get':
        html = etree.HTML(requests.get(page_url, params=param, headers=headers).text)
    else:
        html = etree.HTML(requests.post(page_url, data=param, headers=headers).text)
    data = html.xpath(xpath)
    return not data
