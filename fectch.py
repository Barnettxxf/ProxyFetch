# -*- coding:utf-8 -*-
import random
from DBUtils.PooledDB import PooledDB
import requests
import pymysql
from config_MySQL import LOCALCONFIG
"""
免费代理网址
http://www.kxdaili.com/             //新增待爬
http://proxy.mimvp.com/free.php     // 已爬
http://www.xicidaili.com/wn/        // 已爬
http://www.ip181.com/               // 一个帖子，还行
https://www.kuaidaili.com/ops/proxylist/1/  //新增待爬
http://www.swei360.com/?page=1      //新增待爬
http://www.sslproxies.org/           // 新增待爬
http://www.us-proxy.org/             // 新增待爬
http://free-proxy-list.net/uk-proxy.html'      // 新增待爬
http://www.socks-proxy.net/'         // 新增待爬
http://www.data5u.com/free/index.shtml
http://www.data5u.com/free/gngn/index.shtml
http://www.data5u.com/free/gnpt/index.shtml
http://www.data5u.com/free/gwgn/index.shtml
http://www.data5u.com/free/gwpt/index.shtml
https://hidemy.name/en/proxy-list/
"""


class ProxyNewIp(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
    }

    _pool = None

    def __init__(self, test_url=None):
        # self.conn = pymysql.connect(**LOCALCONFIG)
        self.conn = ProxyNewIp.__get_conn()
        self.cursor = self.conn.cursor()
        self.test_url = test_url

    @staticmethod
    def __get_conn():
        if ProxyNewIp._pool is None:
            ProxyNewIp._pool = PooledDB(creator=pymysql, mincached=1, maxcached=20, maxconnections=20, **LOCALCONFIG)
        return ProxyNewIp._pool.connection()

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