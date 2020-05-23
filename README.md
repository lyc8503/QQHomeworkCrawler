# QQHomeworkCrawler
QQ群回家作业下载爬虫. 

#### 用处
用来下载 QQ 群中你上交的作业和老师的评语和批阅记录, 便于保存和整理. 

#### 使用方法
按照提示输入抓包获得的 cookie 和 bkn 两个参数(注意: QQ 默认不会走系统 HTTP 代理, 需要手动设置代理, 推荐使用 Fiddler 抓包), 同时输入布置的作业所在群的群号即可. 

数据会保存到程序运行目录下的 sqlite3 数据库中和 downloaded 文件夹中. 

get_all.py 是获取本群所有人的作业记录并保存, 需要登陆的账号有管理员权限.

get_self.py 是获取自己所有作业记录并保存, 只需要登陆自己的账号即可, 无需是管理员.

两段代码最后保存的 sqlite3 文件格式不太一样...

自己看一下代码应该很容易明白数据保存的格式.(我就懒得写了 :P)
