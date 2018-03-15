# -*- coding:utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fectch_goubanjia import Proxygoubanjia
from fectch_mimvp import Proxymimvp
from fectch_xici import ProxyxiciIp

li = [Proxygoubanjia, Proxymimvp, ProxyxiciIp]

p_list = []

for c in li:
    p_list.append(c())

for p in p_list:
    p.update()
    if hasattr(p, 'save_image'):
        p.save_image()

for p in p_list:
    p.close()

