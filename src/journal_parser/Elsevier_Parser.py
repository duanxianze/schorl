# coding:utf-8
"""
@file:      Elsevier_Parser.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-06 12:16
@description:
            用于解析elsevier出版社的文章详情页
            域名：http://www.sciencedirect.com/science/article/pii/xxxx
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from crawl_tools.request_with_proxy import request_with_random_ua
from bs4 import BeautifulSoup
from src.db_config import new_db_cursor

class ElsevierDetailPageParser:
    def __init__(self, article_page_url, driver):
        driver.get(article_page_url)
        if 'sciencedirect' not in article_page_url:
            raise Exception(
                '[Error] in Elsevier_Parser:\n\tUrl pattern is wrong.')
        self.soup = BeautifulSoup(driver.page_source, 'lxml')
        self.__keywords = ''

    @property
    def pdf_url(self):
        try:
            link = self.soup.select_one("#pdfLink")['href']
            if 'ShoppingCartURL' in link:
                # 被指向支付页面，不是在学校ip里的情况
                return None
            else:
                return link
        except Exception as e:
            print('[Error] in Elsevier_Parser.pdf_url():{}'.format(str(e)))
            #print('The url of issue is:{}\n'.format(link))
            return None

    @property
    def keywords(self):
        keywords_locate = None
        try:
            keywords_locate = self.soup.find_all(class_='keyword')
            for i in keywords_locate:
                self.__keywords = self.__keywords + \
                    '{}, '.format(i.get_text().replace(';', ', '))
        except:
            pass
        if self.__keywords:
            return self.__keywords, 'Acquired'
        else:
            return None, 'Keywords not found'


class ElsevierAllItemsPageParser:
    '''
        sample_url: http://www.sciencedirect.com/science/journal/15708268
    '''
    def __init__(self,html_source=None):
        self.soup = BeautifulSoup(html_source,'lxml')
        self.nav = self.soup.select_one('#volumeIssueData')

    @property
    def secs(self):
        return self.soup.select_one('.articleList').select('.detail')

    @property
    def volume_area_links(self):
        volume_a_tags = self.nav.select('.volLink')
        return list(map(lambda x:'http://www.sciencedirect.com'+x['href'],volume_a_tags))

    @property
    def volume_divs(self):
        return self.nav.select('.currentVolumes')[1:]

    @property
    def volume_links(self):
        return list(map(lambda x:'http://www.sciencedirect.com'+x.select_one('a')['href'],self.volume_divs))


class ElsevierAricle:
    def __init__(self,sec):
        self.sec = sec
        self.cur = new_db_cursor()

    @property
    def origin_title(self):
        return self.sec.select_one('.title').text

    @property
    def title(self):
        tit = self.origin_title
        if 'Original Research Article' == self.type:
            tit = tit[:-25]
        return tit

    @property
    def abstract_url(self):
        return self.sec.select_one('.absLink')['data-url']

    @property
    def abstract(self):
        #访问abstract_url直接生成
        try:
            resp = request_with_random_ua(self.abstract_url)
            return BeautifulSoup(resp.text,'lxml').select_one('.paraText').text
        except Exception as e:
            print('[ERROR] in Elsevier Parser:abstract():\n{}'.str(e))
            return None

    @property
    def pdf_url(self):
        url = self.sec.select_one('.extLinkBlock').select_one('.cLink')['href']
        if '.pdf' in url:
            return url
        else:
            print('[ERROR] in Elsevier Parser:pdf_url()')
            return None

    @property
    def authors(self):
        return self.sec.select_one('.authors').text.split(',')

    @property
    def type(self):
        if 'Original Research Article' in self.origin_title:
            return 'Original Research Article'
        if 'Review Article' in self.origin_title:
            return 'Review Article'
        return None

    @property
    def link(self):
        return self.sec.select_one('.title').find('a')['href']

    @property
    def id_by_journal(self):
        return self.link.split('/')[-1]

    def save_article(self):
        if not self.type:
            type('Article Type Error')
            return False
        pass

    def save_scholar(self):
        pass

    def relation_is_saved(self):
        pass

    def save_scholar_category_realtion(self):
        pass

    def save_to_db(self):
        if self.save_article():
            if self.save_scholar():
                self.save_scholar_category_realtion()

    def show_in_cmd(self):
        print('origin_title:{}'.format(self.origin_title))
        print('title:{}'.format(self.title))
        print('abstract:{}'.format(self.abstract))
        print('pdf_url:{}'.format(self.pdf_url))
        print('authors:{}'.format(self.authors))
        print('type:{}'.format(self.type))
        print('link:{}'.format(self.link))
        print('abstract_url:{}'.format(self.abstract_url))
        print('id_by_journal:{}'.format(self.id_by_journal))


if __name__ == "__main__":
    '''
    ep = ElsevierDetailPageParser(
        article_page_url='http://www.sciencedirect.com/science/article/pii/S1090780708001389'
    )
    print(ep.pdf_url)
    '''

    text = '<li class="detail"><ul class="article"><li class="selection"><input aria-labelledby="title_S1570826816300166" class="checkBox" name="art" style="padding-left:6px;" type="checkbox" value=" 1-s2.0-S1570826816300166"/></li><li class="title "><h4><a class="cLink artTitle S_C_artTitle " data-docsubtype="fla" href="http://www.sciencedirect.com/science/article/pii/S1570826816300166" id="title_S1570826816300166" querystr="?_rdoc=5&amp;_fmt=high&amp;_origin=PublicationURL&amp;_srch=hubEid(1-s2.0-S1570826816X00042)&amp;_docanchor=&amp;_ct=7&amp;md5=755c8390bdd7739ca7ff0a633f22293c">LHD 2.0: A text mining approach to typing entities in knowledge graphs</a></h4><span class="articleTypeLabel">Original Research Article</span></li><li class="source "><i>Pages 47-61</i></li><li class="authors ">TomÃ¡Å¡ Kliegr, OndÅej Zamazal</li><li class="external "><div class="txt external "><ul class="extLinkBlock extLinkBlockJrnl"><li><a aria-controls="abs_S1570826816300166" aria-describedby="title_S1570826816300166" aria-expanded="false" class="absLink" data-type="abstract" data-url="http://www.sciencedirect.com/science/preview/abstract?_rdoc=5&amp;_origin=PublicationURL&amp;_srch=hubEid(1-s2.0-S1570826816X00042)&amp;_ct=7&amp;_zone=rslt_list_item&amp;_fmt=full&amp;_pii=S1570826816300166&amp;_issn=15708268&amp;_tab=afr&amp;absLinks=y&amp;md5=27959384d39b49db15150953066297aa" href="#" role="button"><span class="arrowSide"></span><span class="preTxt">Abstract</span></a></li><li><a aria-describedby="title_S1570826816300166" class="cLink" href="http://www.sciencedirect.com/science/article/pii/S1570826816300166/pdfft?md5=dfcf27ef270fe39bc8f1caf1fede4d2f&amp;pid=1-s2.0-S1570826816300166-main.pdf" querystr="?_origin=PublicationURL&amp;_zone=rslt_list_item" rel="nofollow" target="_blank"><span class="pdfIconSmall"> </span>PDF (1010 K)</a></li>\
            <li><a class="mmcLinkSprite" clink="" data-docsubtype="fla" href="http://www.sciencedirect.com/science/article/pii/S1570826816300166#MMCvFirst" id="title_S1570826816300166" querystr="?_rdoc=5&amp;_fmt=high&amp;_origin=PublicationURL&amp;_srch=hubEid(1-s2.0-S1570826816X00042)&amp;_docanchor=&amp;_ct=7&amp;md5=755c8390bdd7739ca7ff0a633f22293c" s_c_arttitle=""><span class="mmcTxt">Supplementary content</span></a></li></ul><div class="previewBox abstract hidden" id="abs_S1570826816300166"></div><div class="previewBox rabstract hidden" id="rabs_S1570826816300166"></div><div class="previewBox gabstract hidden" id="gabs_S1570826816300166"></div></div></li><li class="accessBlock colLast"><span alt="Entitled to full text" class="dsub_article_sci_dir sci_dir" title="Entitled to full text"> <span class="offscreen">Entitled to full text</span></span></li></ul></li>'

    sec = BeautifulSoup(text,'lxml')
    ElsevierAricle(sec).show_in_cmd()