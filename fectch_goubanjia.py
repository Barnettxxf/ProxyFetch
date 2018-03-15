from scrapy import Selector
from fectch import ProxyNewIp
from selenium import webdriver
import re
import datetime


class Proxygoubanjia(ProxyNewIp):

    def __init__(self, text_url=None):
        super(Proxygoubanjia, self).__init__(text_url)
        option = webdriver.ChromeOptions()
        option.set_headless()
        self.driver = webdriver.Chrome(chrome_options=option)

    def fecth(self, soup: Selector):
        table = soup.css('tbody > tr')
        for each in table:
            item = {}

            ip_text_list = each.xpath('.//td[1]/*').extract()
            ip = self.parse_ip_list_text(ip_text_list)

            port = each.css('td.ip > span.port::text').extract()[0]
            proxy_type = each.css('td a ::text').extract()[1]
            speed = each.css('td:nth-child(6)::text').extract()[0][:-2]

            time_text = each.css('td:nth-child(7)::text').extract()[0]
            date_time = self.parse_date_time(time_text)

            item['ip'] = ip
            item['port'] = port
            item['proxy_type'] = proxy_type
            item['speed'] = speed
            item['date_time'] = date_time
            print(item)
            self.insert_mysql(item)

    def download(self):
        self.driver.get('http://www.goubanjia.com/')
        with open('goubanjia.html', 'w') as f:
            f.write(self.driver.page_source)
        yield Selector(text=self.driver.page_source)

    def insert_mysql(self, item):
        insert_sql = """
                    INSERT INTO proxygoubanjia (ip, port, proxy_type, speed, date_time) VALUES (%s,%s,%s,%s,%s)
                    ON duplicate KEY UPDATE port=VALUES (port), proxy_type=VALUES (proxy_type), speed=VALUES (speed),
                    date_time=VALUES (date_time);
                """
        params = (
            item['ip'], item['port'], item['proxy_type'], item['speed'], item['date_time']
        )
        self.cursor.execute(insert_sql, params)
        self.conn.commit()

    def parse_ip_list_text(self, ip_list_text):
        li = ip_list_text
        re_1 = re.compile('<span>(.+)</span>')
        re_2 = re.compile('inline-block;">(.+)</')
        ip = ''
        for each in li:
            if re_1.search(each):
                text = re_1.search(each).group(1)
            elif re_2.search(each):
                text = re_2.search(each).group(1)
            else:
                text = ''
            ip += text
        # print('ip: ', ip)
        return ip

    def parse_date_time(self, time_text):
        dig = int(re.search('(.)分钟前', time_text).group(1))
        now_time = datetime.datetime.now()
        yes_time = now_time + datetime.timedelta(minutes=-dig)
        yes_time = str(yes_time).split('.')[0]
        return yes_time

    def close(self):
        self._mysql_close()
        self.driver.quit()


if __name__ == '__main__':
    t = Proxygoubanjia()
    t.update()
    t.close()
