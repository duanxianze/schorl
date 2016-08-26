# scholar_articles

[Google Schloar](http://scholar.google.com)

* title
* year
* citations_count
* link
* bibtex
* resource_type
* resource_link
* summary(abstract)
* google_id

# 准备工作

## virtualenv

* virtualenv安装: `pip install virtualenv`
* 创建python2.7虚拟环境: `virtualenv venv` （使用这步命令的前提是你的机器中python命令的版本默认是2.7）
* 启动虚拟环境: `source venv/source/activate`
* 安装依赖: `pip install -r requirements.txt`

注意: 在pip install 安装依赖之前，确保启动了虚拟环境，这样才不会把全局依赖和虚拟环境的依赖混淆

#Datebase
接手前articles表中有314037条数据
但是最大id为314060
截止到2016-8-26，大约46w

#Module
##条目的初步创建

### ArticleSpider.py
包含:
- 获取搜索结果urls的`ScholarSearch`类
- 爬虫主控制器`ArticleSpider`类

工作原理：
- spider从db中检索出scholar姓名
- 交予`ScholarSearch`得到url，访问后得到源码交给`HtmlParser`模型

### parse_html.py
包含：
- 解析搜索结果页面的`HtmlParser`类，
- 逻辑上的`Article`类，包括属性的获取，数据库保存

工作原理：
- paser解析出文章元素列表`secs`
- 分别生成`Article`对象获得所有文章属性，存入数据库

##异步获取细节
### download.py
- 仅包含一个`pdf_downloader`类
- 从远程db中检索出`存在且未下载`的pdf_url条目，存于本地
- 可脱离于主程序，在宿机器上运行

### bibtex.py
NULL
##任务进程监控
### WacthDog.py&为各项任务定制的**watchdog.py
- 用到`psutil`，`subprocess`包，获取某项进程的各种状态属性
- 某项具体的task作为watchdog的subprocess运行，启动直接运行watchdog即可
- watchdog和task并行不阻塞
- 主类包含`进程级别的task异常`的处理方法，杀进程，重启进程，管理员邮件提示等
- 子类具体写`task逻辑异常的识别`，如数据量异常等
- 子类再写一些关键数据的打印，交互性的东西，以及数据的监控统计之类
