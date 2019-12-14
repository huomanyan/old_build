#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by PyCharm.
# @Project: Article_Crawler
# @File: parse_page_body.py
# @Description: 解析网页，抽取文字和图片链接
# @Time: 2018/11/26 10:41
# @Author: ljz

import hashlib
import re
from html.parser import HTMLParser

import requests


class _DeHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._text = []
        self._img = []
        self.ignore_tag_list = ['script', 'style']
        self.allowed_tag_list = ['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'a', 'code']

    def handle_data(self, data):
        content = data.strip()
        if self.lasttag not in self.ignore_tag_list:
            self._text.append(content)

    def handle_starttag(self, tag, attrs):
        if tag in self.allowed_tag_list:
            if tag == 'pre':
                self._text.append('\n```\n')
            elif tag == 'h1':
                self._text.append('\n# ')
            elif tag == 'h2':
                self._text.append('\n## ')
            elif tag == 'h3':
                self._text.append('\n### ')
            elif tag == 'h4':
                self._text.append('\n#### ')
            elif tag == 'h5':
                self._text.append('\n##### ')
            elif tag == 'h6':
                self._text.append('\n###### ')
            elif tag == 'a':
                self._text.append('[')
            elif tag == 'code':
                self._text.append('`')
            else:
                self._text.append('\n')

    def handle_endtag(self, tag):
        if tag in self.allowed_tag_list:
            if tag == 'pre':
                self._text.append('\n```\n')
            elif tag == 'a':
                self._text.append(']()')
            elif tag == 'code':
                self._text.append('`')
            else:
                self._text.append('\n')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._text.append('\n')
        if tag == 'img':
            img_url_md5 = hashlib.md5({item[0]: item[1] for item in attrs}['src'].encode(encoding='UTF-8')).hexdigest()
            self._text.append('\n' + '<img>' + img_url_md5 + '<img>' + '\n')
            self._img.append([img_url_md5, {item[0]: item[1] for item in attrs}['src']])

    def error(self, message):
        pass

    @staticmethod
    def handle_line_feed(origin_text):
        origin_text = re.sub('\\[(htt.*?)]\\(\\)', '[\\g<1>](\\g<1>)', origin_text)
        # origin_text = re.sub('\\[(?!htt).*]\\(\\)', '\\n', origin_text)
        origin_text = re.sub('\\n{3,}', '\\n\\n', origin_text)

        return origin_text

    def get_text(self):
        return self.handle_line_feed(''.join(self._text).strip())

    def get_img(self):
        return self._img


def execute_by_url(url):
    parser = _DeHTMLParser()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}
    page_request = requests.get(url, headers=headers)
    page_request.encoding = 'utf-8'
    parser.feed(page_request.text)
    parser.close()

    return parser.get_text(), parser.get_img()


def execute_by_content(content):
    parser = _DeHTMLParser()
    parser.feed(content)
    parser.close()

    return parser.get_text(), parser.get_img()


if __name__ == '__main__':
    text, img = execute_by_url('https://it-node.iteye.com/blog/2424288')
    print(text)
    print(img)
