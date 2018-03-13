# -*- coding:utf-8 -*-
import requests
from scrapy import Selector
from ProxyFecth.fectch import ProxyNewIp


class ProxyxiciIp(ProxyNewIp):

    default_url = 'http://www.xicidaili.com/wn/{page}'


    def fecth(self, soup):
        results = soup.css('#ip_list tr')
        item = {}

        for result in results[1:]:
            data = result.css('td::text').extract()
            item['ip'] = data[0]
            item['port'] = data[1]
            item['proxy_type'] = data[5]
            item['speed'] = result.css('.bar::attr(title)').extract()[0].split('秒')[0]
            print(item)
            # if not self._checkproxy(item['ip'], item['port']):
            #     continue
            self.insert_mysql(item)

    def download(self):
        pages = range(1, 960)

        for page in pages:
            self._sleep(page)
            print('page: ', page)
            response = requests.get(self.url.format(page=page), headers=self.headers)
            yield Selector(text=response.text)

    def getproxy(self):
        """
        获取1未用过的ip，取出标志为1
        :return: None
        """
        query_sql = """
            SELECT ip,port FROM proxyip WHERE flag != 1 ORDER BY speed limit 1;
        """
        self.cursor.execute(query_sql)
        self.conn.commit()
        data = self.cursor.fetchall()
        for each in data:
            yield each

            # 把取出来的ip对应的flag字段设置为1,避免重复取
            pop_ip = each[0]
            update_sql = """
                UPDATE proxyip SET flag = 1 WHERE ip='{pop_ip}';
            """.format(pop_ip=pop_ip)
            self.cursor.execute(update_sql)
            self.conn.commit()

    def insert_mysql(self, item):
        insert_sql = """
            INSERT INTO proxyhttps (ip, port, proxy_type, speed) VALUES (%s,%s,%s,%s)
            ON duplicate KEY UPDATE port=VALUES (port), proxy_type=VALUES (proxy_type), speed=VALUES (speed);
        """
        params = (
            item['ip'], item['port'], item['proxy_type'], item['speed']
        )
        self.cursor.execute(insert_sql, params)
        self.conn.commit()


if __name__ == '__main__':
    t = ProxyxiciIp()
    t.update()
