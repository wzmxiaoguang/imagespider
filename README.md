# imagespider
今日头条图集爬取

#### 原始版本

spider.py - 带MongoDB数据库储存的原始版本

config.py - spider.py的配置项

#### 无gui生成版本

generate.py - 用于生成exe的版本,不带MongoDB,可自行调整代码为单线程多线程，默认单线程

未修复bug:使用多线程的exe打开后会占用大量资源导致电脑资源不足而死机，直接运行代码则不会有此问题

生成代码： pyinstaller -F generate.py

generate.exe - 生成后的exe文件,可单独运行，无需其它文件，需在cmd中运行以便指定关键字

#### gui版本

generate_gui.py - 用于生成带gui的exe的版本,不带MongoDB,只支持单线程

26f7e7447c84e9053b04e65886cea5ed_jpg.py - 背景图片的base64编码

akashi.ico - 图标文件

26f7e7447c84e9053b04e65886cea5ed.jpg - 背景图片

pic2py.py - 将图片转换为base64编码

仅需要前3个文件即可生成exe

生成代码：pyinstaller -w -F --ico=akashi.ico  generate_gui.py

generate_gui.exe - 生成后的exe，可单独运行，无需其它文件