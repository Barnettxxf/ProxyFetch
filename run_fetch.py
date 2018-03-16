# -*- coding:utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fectch_goubanjia import Proxygoubanjia
from fectch_mimvp import Proxymimvp
from fectch_xici import ProxyxiciIp
import gevent
from gevent import monkey
monkey.patch_all()

li = [Proxygoubanjia, Proxymimvp, ProxyxiciIp]

p_list = []


def run(p):
    p.update()
    if hasattr(p, 'save_image'):
        p.save_image()
    p.close()


for c in li:
    p_list.append(c())

t_list = []
for p in p_list:
    t = gevent.spawn(run, p)
    t_list.append(t)

for t in t_list:
    t.join()

