# -*- coding:utf-8 -*-
import requests
from scrapy import Selector
from fectch import ProxyNewIp


class ProxyxiciIp(ProxyNewIp):

    default_url = 'http://www.xicidaili.com/wn/'

    def fecth(self, soup):
        results = soup.css('#ip_list tr')
        item = {}
        num = 0
        for result in results[1:]:
            if num > 25:
                break
            data = result.css('td::text').extract()
            item['ip'] = data[0]
            item['port'] = data[1]
            item['proxy_type'] = data[5]
            item['speed'] = result.css('.bar::attr(title)').extract()[0].split('秒')[0]
            item['date_time'] = '20' + result.css('td:nth-child(10)::text').extract()[0]
            print(item)
            # if not self._checkproxy(item['ip'], item['port']):
            #     continue
            if item['proxy_type'] == 'HTTPS':
                self.insert_mysql(item)
            num += 1

    def download(self):
            response = requests.get(self.default_url, headers=self.headers)
            yield Selector(text=response.text)

    def insert_mysql(self, item):
        insert_sql = """
            INSERT INTO proxyxici (ip, port, proxy_type, speed, date_time) VALUES (%s,%s,%s,%s,%s)
            ON duplicate KEY UPDATE port=VALUES (port), proxy_type=VALUES (proxy_type), speed=VALUES (speed),
            date_time=VALUES (date_time);
        """
        params = (
            item['ip'], item['port'], item['proxy_type'], item['speed'], item['date_time']
        )
        self.cursor.execute(insert_sql, params)
        self.conn.commit()


if __name__ == '__main__':
    t = ProxyxiciIp()
    t.update()
    t.close()
