# scholar_articles

##`History`
### 2016-4开始GoogleScholar方向工作
- 接手前articles表中有314037条数据，最大id为314060
- 截止到2016-9-11，大约52w，单机日增量3k-9k，电磁学的学者从谷歌上检索完成，大部分条目已存，只爬谷歌最近的增量
### 2016-9-25起启动杂志社方向爬虫
- 截止到2016-10-1，大约200w，单机日增量30w-50w
- publisher进度:
 IEEE（80家journal，文章总量30w，进度[80/80]）
 
 Springer（700家journal，文章总量400w-600w，进度[94/700]）
 
 Elsevier（1200家journal，文章总量700w-1000w，进度[76/1200]）
 
##`JournalTask`

###数据关系为：
- `publisher->journal->volume->article`
- `出版社->期刊->卷->文章`

- 一个出版社一个解析器

###解析器包括三层：

- 数据库中保存的journal site_source解析至journal主页
（少部分直接保存的就是journal主页，大部分需要一些转换）

- journal主页解析得到所有volume_link

- 针对每个volume_link页写解析器，得到该页所有article
（注意多页的问题，但大部分情况是一页，一个杂志一卷，可能就是一年半载，不会有多少文章，至多几十篇）

- 以上三步是全过程，
     前两部都写在`JournalTask文件夹`的某某spider里
     注意继承`JournalSpider`基类
     第三部写在`journal_parser文件夹`的某某parser里
     注意继承`JournalArticle`基类


##`Google Schloar`

* title
* year
* citations_count
* link
* bibtex
* resource_type
* resource_link
* summary(abstract)
* google_id


###条目初步创建

#### ArticleSpider.py
包含:
- 获取搜索结果urls的`ScholarSearch`类
- 爬虫主控制器`ArticleSpider`类

工作原理：
- spider从db中检索出scholar姓名
- 交予`ScholarSearch`得到url，访问后得到源码交给`HtmlParser`模型

#### parse_html.py
包含：
- 解析搜索结果页面的`HtmlParser`类，
- 逻辑上的`Article`类，包括属性的获取，数据库保存

工作原理：
- paser解析出文章元素列表`secs`
- 分别生成`Article`对象获得所有文章属性，存入数据库

###异步获取细节
#### pdf_download.py
- 仅包含一个`pdf_downloader`类
- 从远程db中检索出**存在且未下载**的pdf_url条目，存于本地
- 可脱离于主程序，在宿机器上运行

####**journal_pdf_url_generate.py
-  某些pdf_url谷歌无法拿到，需要版权
-  针对每一学校购置版权的杂志社，写好parser，由db中的title，去搜索页检索，得到pdf_url，反馈给db

#### bibtex.py
包含:
- 爬虫控制器`BibtexSpider`类
- 逻辑上的`Bibtex`类，包括属性的获取，数据库保存

工作原理：
- 从db中检索出未填充好bibtex的article条目
- 根据google_id,规则匹配url，进入中间页，寻找bibtex页面的url
- 进入bibtex页面，获取完毕


