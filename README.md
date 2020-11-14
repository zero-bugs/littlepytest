# littlepytest

##配置pip代理

##Linux，在~/.pip/pip.conf文件中添加（不存在时添加）
##windows，再%APPDATA%\pip\pip.ini文件添加（不存在时添加）

[global]
timeout = 6000
index-url = http://pypi.douban.com/simple
trusted-host = pypi.douban.com


####其他站点信息
  阿里云 http://mirrors.aliyun.com/pypi/simple/
  中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/
  豆瓣(douban) http://pypi.douban.com/simple/ pypi.douban.com
  清华大学 https://pypi.tuna.tsinghua.edu.cn/simple/
