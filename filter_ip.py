# -*- coding:utf-8 -*-
import random

import pymysql
import pandas as pd
import time

from ProxyFecth.config_MySQL import LOCALCONFIG
from requests.adapters import HTTPAdapter
import requests
from sqlalchemy.engine import create_engine
import logging
import json
# import gevent
password = LOCALCONFIG['password']
count = 0
engine = create_engine(f'mysql+pymysql://root:{password}@localhost:3306/jobdata')
request_retry = HTTPAdapter(max_retries=3)


class FilterIp(object):

    headers = {
        'Referer': 'https://www.lagou.com/jobs/list_python%E7%88%AC%E8%99%AB?labelWords=&fromSearch=true&suginput=',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
    }

    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]


    def spawn_run(self):
        self.run()

    def run(self):
        for ip, port in self._get_data():
            self._filter(ip, port)

    def _filter(self, ip, port):
        global count
        count += 1
        if self._checkproxy(ip, port):
            with open('filter_ip.csv', 'w') as f:
                f.write(ip + ':' + port + '\n')
            logging.info(f'{count}-Succeeded!{ip}:{port}')
        else:
            logging.error(f'{count}-Failed!{ip}:{port}')

    def _checkproxy(self, ip, port):
        test_url = 'https://www.lagou.com/jobs/positionAjax.json?city=%E6%B7%B1%E5%9C%B3&needAddtionalResult=false&isSchoolJob=0'
        # proxy_url = f'123.53.86.158:24866'
        proxy_url = ip + ':' + port
        proxy_dict = {'https': proxy_url}
        try:
            time.sleep(3)
            self.headers['User-Agent'] = random.choice(self.user_agent_list)
            response = requests.get(test_url, headers=self.headers, proxies=proxy_dict, timeout=10)
            if response.status_code == 200:
                print(response.text[:67])
                content = json.loads(response.text)
                if content['success'] is True:
                    return True
                else:
                    return False
            elif response.status_code == 500:
                return False
            else:
                print(response)
                return False
            # response.encoding = 'utf-8'
            # content = json.loads(response.text)
            # if not content['success'] == 'true':
            #     logging.error(content['msg']+'|'+content['clientIp'])
            #     return False
        except Exception as e:
            logging.error(e)
            return False

    def _get_data(self):
        datas = pd.read_sql('proxyhttps', engine)
        for i in range(0, datas.shape[0]):
            # print(datas.loc[i, ['ip', 'port']].values[0])
            yield datas.loc[i, ['ip', 'port']].values[0], datas.loc[i, ['ip', 'port']].values[1]


    def _test(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
        }
        response = requests.get('https://www.huxiu.com/', headers=headers, proxies={'http': '127.0.0.1:8888'},
                                verify=False)
        response_1 = requests.get('http://www.meizi.com/', proxies={'http': '127.0.0.1:8888'})
        print(response)
        print(response_1)
        print(response.text)
        print(response_1.text)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='filter.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    start = time.time()
    logging.info('########################Filtering Now########################')
    t = FilterIp()
    t.spawn_run()
    logging.info('########################Finished Yet########################')
    print('******************Cost {} seconds******************'.format(time.time() - start))
