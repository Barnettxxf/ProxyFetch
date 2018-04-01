# ProxyFetch
#### 简介

​	使用python的requests库，实现对三个IP代理网站的免费IP代理的爬取，使用协程进行运行三个爬虫加快整体爬取速度,使用Ubuntu的cron服务来定时刷新MySQL数据库里面的数据，并检测获得的IP是否可用并刷选保留可用IP代理。另外写了一个[ProxyPool代理爬虫项目](https://github.com/Barnettxxf/ProxyPool)可以通过简单的添加xpath页面解析规则和添加item清理即可完成一个新代理网站的开发，这里提到爬取的代理网站[ProxyPool代理爬虫项目](https://github.com/Barnettxxf/ProxyPool)里都有，详情可到项目里看~

​	爬取的代理网站有网站一www.goubanjia.com，网站二[proxy.mimvp.com](proxy.mimvp.com)和网站三www.xicidaili.com三个网站。

​	网站一对页面数据进行加密了，所以直接用selenium来获取js渲染后的页面。另外该网站对IP显示加入了噪音，最后采用正则获取IP地址。

​	网站二端口字段的值用图片显示，用简单的向量空间搜索算法进行图片识别获得端口号。

​	网站三很简单...



## Requirements

​	Ubuntu 17.10

​	python3 (anaconda3)

​	requests

​	gevent

​	DButils

​	Pillows

​	以上第三方库可以使用requirements直接安装，`pip install -r requirements`, 即可配置python环境需求，此外还需要用到MySQL数据库。



## 使用方法

​	配置好环境，直接运行run_fetch.py即可



## 说明

​	仅作学习交流使用！





​		

