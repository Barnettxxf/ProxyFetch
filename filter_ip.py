# -*- coding:utf-8 -*-

import pymysql
import time
from config_MySQL import MyAliyunServer as CONFIG
import requests
from threading import Thread
from queue import Queue
from urllib3 import disable_warnings; disable_warnings()

result = Queue()

class GetIP(object):

    test_url = 'https://www.baidu.com'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36'}
    tables = ['proxymimvp', 'proxyxici', 'proxygoubanjia']

    def __init__(self, timeout=10):
        self.conn = pymysql.connect(**CONFIG)
        self.cursor = self.conn.cursor()
        self.timeout = timeout

    @property
    def ip_list(self):
        ip_list = []
        while len(ip_list) < 7:
            result = self.get_ip()
            ip_list.extend(result)
        return ip_list

    def get_ip(self):
        tables = self.tables
        datas = []
        for table_name in tables:
            data = self.get_data(table_name)
            data = self.filter_data(table_name, data)
            datas.append(data)
        result = []
        for i in range(len(datas)):
            result.extend(datas[i])
        return result

    def check(self, ip, port):
        test_url = self.test_url
        proxies = {'https': ip+':'+port}
        print('Testing: ', ip+':'+port)
        try:
            requests.get(test_url, headers=self.headers, proxies=proxies, timeout=self.timeout, verify=False)
        except Exception as e:
            return False
        print('Suceeded: ', ip+':'+port)
        return True

    def filter_data(self, table_name, data):
        new_datas = []
        tasks = []
        for each in data:
            self.update_db(table_name, each[0])
            t = Thread(target=self._filter_date, args=(table_name, each, ))
            tasks.append(t)
        for t in tasks:
            t.start()
        for t in tasks:
            t.join()
        while not result.empty():
            new_datas.append(result.get())
        return new_datas

    def _filter_date(self, table_name, each):
        if self.check(each[0], each[1]):
            result.put(each)
            self.set_enable_flag(table_name, each[0])

    def get_data(self, table_name):
        select_sql = """
            SELECT ip, port, proxy_type FROM %s WHERE flag=0 ORDER BY 
            date_time desc limit 10;
            """ % table_name
        self.execute(select_sql)
        data = self.cursor.fetchall()
        new_data = []
        for each in data:
            if ('HTTPS' not in each[2]) and ('https' not in each[2]):
                continue
            else:
                new_data.append(each)
        return new_data

    def update_db(self, table_name, ip):
        update_sql = """
                    UPDATE {} SET flag=1 WHERE ip='{}'
                    """.format(table_name, ip)
        self.execute(update_sql)

    def set_enable_flag(self, table_name, ip):
        update_sql = """
                    UPDATE {} SET flag=2 WHERE ip='{}'
                    """.format(table_name, ip)
        self.execute(update_sql)

    def execute(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        # self.recover()
        self.cursor.close()
        self.conn.close()

    def recover(self):
        for each in self.tables:
            recover_sql = """
            update %s set flag=0 where flag!=0;     
        """
            self.execute(recover_sql % each)


if __name__ == '__main__':
    t = GetIP(4)
    start_time = time.time()
    ds = t.ip_list
    print('ruesult: ', ds)
    print('Total cost {} seconds'.format(time.time() - start_time))
    t.close()

