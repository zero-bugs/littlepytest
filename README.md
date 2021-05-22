## littlepytest
## 安装black格式化工具
## Linux，在~/.pip/pip.conf文件中添加（不存在时添加）
## windows，再%APPDATA%\pip\pip.ini文件添加（不存在时添加）
可以通过如下命令查看配置文件搜索路径
```
pip3 -v config list
```

## 编辑pip.ini文件
#### 样例1
```
[global]
timeout = 6000
index-url = http://pypi.douban.com/simple
[install]
trusted-host = pypi.douban.com
```
#### 样例2
```
[global]
timeout = 6000
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host=mirrors.aliyun.com
```

#### 其他站点信息
- 阿里云 http://mirrors.aliyun.com/pypi/simple/
- 中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/
- 豆瓣(douban) http://pypi.douban.com/simple/ pypi.douban.com
- 清华大学 https://pypi.tuna.tsinghua.edu.cn/simple/


## 安装
命令1
```
python -m pip3 --proxy=http://username:password@host:port install black
```
或者
```
pip3 --proxy=http://username:password@host:port -install black
```
注：使用python3时，需要使用对应的pip3
