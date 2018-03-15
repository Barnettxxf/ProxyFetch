# -*- coding:utf-8 -*-
import random

import requests
from urllib.parse import urljoin, unquote

import time
from scrapy import Selector
import pymysql
from config_MySQL import LOCALCONFIG

"""
免费代理网址
http://www.kxdaili.com/             // 这个不错
http://proxy.mimvp.com/free.php     // 要会员的，不然资源少，放弃
http://www.xicidaili.com/wn/        // 资源不错，有很多
http://www.ip181.com/               // 一个帖子，还行
http://www.httpdaili.com/mfdl/      // 要购买的，放弃
http://www.66ip.cn/                 // 连接不上
"""


class ProxyNewIp(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
    }

    def __init__(self, test_url=None):
        self.conn = pymysql.connect(**LOCALCONFIG)
        self.cursor = self.conn.cursor()
        self.test_url = test_url

    def update(self, url=None):
        """
        更新代理数据库,换网址的话请继承类并重写_download和_fecth方法
        :param url: 默认xici代理网页，换网址请重新写解析方法，即_download和_fecth方法
        :return:
        """
        if url != None:
            self.url = url
        soups = self.download()
        for soup in soups:
            self.fecth(soup)

    def close(self):
        self._mysql_close()

    def fecth(self, soup):
        pass

    def download(self):
        yield

    def getproxy(self):
        pass

    def _checkproxy(self, ip, port):
        test_url = self.test_url
        if test_url is None:
            raise Exception('If you want to check proxy, you should set you test_url first.')
        proxy_url = f'http://{ip}:{port}'
        proxy_dict = {
            'http': proxy_url,
            'https': proxy_url
        }
        try:
            response = requests.get(test_url, self.headers, proxies=proxy_dict)
        except:
            return False
        return True

    def insert_mysql(self, item):
        pass

    def _mysql_close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    t = ProxyNewIp()
    t.update()
    t.close()