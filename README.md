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

===
articles表中有314037条数据
但是最大id为314060
