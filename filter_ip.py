# -*- coding:utf-8 -*-
import pandas as pd
import time
from ProxyFecth.config_MySQL import LOCALCONFIG
from requests.adapters import HTTPAdapter
import requests
from sqlalchemy.engine import create_engine
import logging
import threading


password = LOCALCONFIG['password']
count = 0
engine = create_engine(f'mysql+pymysql://root:{password}@localhost:3306/jobdata')
request_retry = HTTPAdapter(max_retries=3)


class FilterIp(object):

    def spawn_run(self):
        data_list = self._get_data()
        tasks = []
        for i in range(len(data_list)):
            task = threading.Thread(target=self.run, args=(data_list[i],))
            tasks.append(task)
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()

    def run(self, data):
        for i in range(data.shape[0]):
            ip, port = data.loc[i, ['ip', 'port']].values[0], data.loc[i, ['ip', 'port']].values[1]
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
        test_url = 'https://www.baidu.com'
        # proxy_url = f'123.53.86.158:24866'
        proxy_url = ip + ':' + port
        proxy_dict = {'https': proxy_url}
        try:
            response = requests.get(test_url, headers=self.headers, proxies=proxy_dict, timeout=5)
        except Exception as e:
            logging.error(e)
            return False
        return True

    def _get_data(self):
        data = pd.read_sql('proxyhttps', engine)
        size = 10
        num = data.shape[0] // size + 1
        print(num)
        data_list = []
        for i in range(1, size):
            new = data.loc[((i - 1) * num):(i * num), :]
            new = new.reset_index(drop=True)
            data_list.append(new)
        return data_list

    def _test(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36',
        }
        response = requests.get('https://www.huxiu.com/', headers=headers, proxies={'http': '127.0.0.1:8888'})
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
