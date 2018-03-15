# -*- coding:utf-8 -*-
import os
import requests
from scrapy import Selector
from fectch import ProxyNewIp
from urllib.parse import urljoin
from caphcat_identify import guess


class Proxymimvp(ProxyNewIp):
    base_url = 'https://proxy.mimvp.com/'
    target_url = 'https://proxy.mimvp.com/free.php?proxy=in_tp'
    image_dir = os.getcwd() + '/image/'

    def __init__(self, test_url=None):
        super(Proxymimvp, self).__init__(test_url)

    def fecth(self, soup):
        image_urls = soup.css('div.free-content > div > table > tbody > td.tbl-proxy-port > img::attr(src)').extract()
        port_images = []
        for url in image_urls:
            new = urljoin(self.base_url, url)
            port_images.append(new)
        ips = soup.css('div.free-content > div > table > tbody > td.tbl-proxy-ip::text').extract()
        proxy_types = soup.css('div.free-content > div > table > tbody > td.tbl-proxy-type::text').extract()
        speeds = soup.css('div.free-content > div > table > tbody > td.tbl-proxy-pingtime::attr(title)').extract()
        date_time = soup.css('div.free-content > div > table > tbody > td.tbl-proxy-checkdtime::text').extract()

        for i in range(len(ips)):
            item = {}
            item['ip'] = ips[i]
            item['port'] = port_images[i]
            item['proxy_type'] = proxy_types[i]
            item['speed'] = speeds[i].split('秒')[0]
            item['date_time'] = date_time[i]
            self.insert_mysql(item)

    def download(self):
        response = requests.get(self.target_url, headers=self.headers)
        yield Selector(text=response.text)

    def insert_mysql(self, item):
        insert_sql = """
                    INSERT INTO proxymimvp (ip, port_image, proxy_type, speed, date_time) VALUES (%s,%s,%s,%s,%s)
                    ON duplicate KEY UPDATE port=VALUES (port), proxy_type=VALUES (proxy_type), speed=VALUES (speed),
                    date_time=VALUES (date_time);
                """
        params = (
            item['ip'], item['port'], item['proxy_type'], item['speed'], item['date_time']
        )
        self.cursor.execute(insert_sql, params)
        self.conn.commit()

    def getproxy(self):
        pass

    def _identify(self):
        image_names = os.listdir(self.image_dir)
        for each in image_names:
            port_ = guess(self.image_dir+each)
            ip_ = each.split('-')[0]

            update_sql = """
                        UPDATE proxymimvp SET port={port_} WHERE ip='{ip_}'and port is NULL;
                    """.format(port_=port_, ip_=ip_)
            delete_sql = """
                DELETE FROM proxymimvp WHERE speed > 1;
            """
            # print(update_sql)
            self.cursor.execute(update_sql)
            self.cursor.execute(delete_sql)
            self.conn.commit()

    def save_image(self):
        query_sql = """
            SELECT ip, port_image FROM proxymimvp WHERE port is NULL ;
        """
        self.cursor.execute(query_sql)
        self.conn.commit()
        datas = self.cursor.fetchall()
        for each in datas:
            filename = self.image_dir + each[0] + '-' + '.jpg'
            response = requests.get(each[1]).content
            with open(filename, 'wb') as f:
                f.write(response)

        self._identify()
        self.delete_image()

    def delete_image(self):
        files = os.listdir(self.image_dir)
        if len(files) > 50:
            for file in files:
                os.remove(self.image_dir + file)


if __name__ == '__main__':
    t = Proxymimvp()
    t.update()
    t.save_image()
    t.close()

