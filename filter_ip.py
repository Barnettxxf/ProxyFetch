# -*- coding:utf-8 -*-
import datetime

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

    def __init__(self, timeout=10, limit=10):
        self.conn = pymysql.connect(**CONFIG)
        self.cursor = self.conn.cursor()
        self.timeout = timeout
        self.limit = limit
        self.execute("""set SQL_SAFE_UPDATES=0""")

    def save_useful_ip(self):
        datas = self.get_ip()
        for each in datas:
            self._save(each)

    def _save(self, data):
        date_time = str(datetime.datetime.now()).split('.')[0]
        insert_sql = """
            INSERT INTO proxyhttps(ip,port,date_time,timeout) VALUES 
            (%s,%s,%s,%s)
            ON duplicate KEY UPDATE date_time=VALUES (date_time), timeout=VALUES (timeout);
        """
        params = (data[0], data[1], date_time, self.timeout)
        self.execute(insert_sql, params)

    def get_ip(self):
        tables = self.tables
        datas = []
        for table_name in tables:
            data = self.get_data(table_name)
            data = self.filter_data(table_name, data)
            datas.append(data)
        final_data = []
        for i in range(len(datas)):
            final_data.extend(datas[i])
        return final_data

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

    def get_data(self, table_name):
        select_sql = """
            SELECT ip, port, proxy_type FROM %s WHERE flag=0 ORDER BY 
            date_time desc limit %s;
            """ % (table_name, self.limit)
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

    def execute(self, sql, params=None):
        if params is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, params)
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
    t = GetIP(timeout=10, limit=1000)
    start_time = time.time()
    t.save_useful_ip()
    print('Total cost {} seconds'.format(time.time() - start_time))
    t.close()

