# coding:utf-8
from bs4 import BeautifulSoup as bs
'''
@author: panda0
@description: some spiders crawling keywords from journals
'''

# ignore cqvip 中文站点


def cqvip_spider(soup):
    # two kinds of keywords
    classification_locate = None
    keywords_locate = None
    classification = ''
    keywords = ''
    try:
        classification_locate = soup.find_all(class_='datainfo f14')[
            1].find_all('td')[1]
    except:
        pass
    try:
        keywords_locate = soup.find_all(class_='datainfo f14')[
            1].find_all('td')[3]
    except:
        pass
    dict = {}
    if classification_locate:
        classification = classification_locate.get_text().strip().replace('、', ', ')
        dict['classification'] = classification
    if keywords_locate:
        keywords = keywords_locate.get_text().strip().replace('、', ', ')
        dict['keywords'] = keywords

    return(str(dict)) if len(dict) > 0 else None


def sciencedirect_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(class_='keyword')
        for i in keywords_locate:
            keywords = keywords + \
                '{}, '.format(i.get_text().replace(';', ', '))
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def springer_spider(soup):
    # topic
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(class_='abstract-about-subject')
    except:
        pass
    try:
        keywords_locate = soup.find_all(
            class_='Keyword') if not keywords_locate else keywords_locate
    except:
        pass
    if keywords_locate:
        for i in keywords_locate:
            keywords = keywords + \
                '{}, '.format(i.get_text().strip().replace('\n\n\n', ', '))
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def wiley_spider(soup):
    keywords_locate = None
    access_locate = None
    keywords = ''
    # try:
    #     access_locate = soup.find_all(class_ = 'r3-access-container')
    #     print('No access')
    #     return None, 'No access'
    # except:
    #     pass
    try:
        keywords_locate = soup.find_all(class_='article-info__keywords-item')
    except:
        pass
    try:
        keywords_locate = soup.find_all(
            class_='keywordLists') if not keywords_locate else keywords_locate
    except:
        pass
    if keywords_locate:
        for i in keywords_locate:
            keywords = keywords + \
                '{}, '.format(i.get_text().strip().replace(
                    '\n\n\n', ', ').replace(';', ', '))
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def acs_spider(soup):
    keywords_locate = None
    keywords = ''

    try:
        keywords_locate = soup.find_all(class_='keywords')[
            0].find_all(class_='keyword')
    except:
        pass
    if keywords_locate:
        for i in keywords_locate:
            keywords = keywords + '{}, '.format(i.get_text().strip())
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def cnki_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.select(
            'a[href^="http://yuanjian.cnki.com.cn/Search/Result?keyword="]')
    except:
        pass
    if keywords_locate:
        for i in range(len(keywords_locate) - 1):
            if keywords_locate[i].select('strong'):
                keywords = keywords + \
                    '{}, '.format(keywords_locate[i].get_text())
            else:
                pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def arxiv_spider(soup):
    subject_locate = None
    subjects = ''
    try:
        subject_locate = soup.find_all(
            'table')[0].find(class_='primary-subject')
    except:
        pass
    if subject_locate:
        subjects = subject_locate.get_text()
    if subjects:
        return subjects, 'Acquired'
    else:
        return None, 'Keywords not found'


def acm_spider(soup):
    print(soup)
    keywords_locate = None
    keywords = ''
    keywords_locate = soup.find_all(id='tab-body9')
    print(keywords_locate)
    if keywords_locate:
        for i in keywords_locate:
            keywords = keywords + '{}, '.format(i.get_text().strip())
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def theiet_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(id='tabbedpages')[0]\
            .find_all(class_='aboutthisarticle hide tabbedsection')[0]\
            .find_all(class_='meta-value')
        for item in keywords_locate:
            for each in item.find_all('a'):
                keywords = keywords + each.get_text() + ','
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


# a dict mapping sites and spiders
spider_pool = {
    # 'cqvip': cqvip_spider,
    'acs': acs_spider,
    'cnki': cnki_spider,
    'sciencedirect': sciencedirect_spider,
    'springer': springer_spider,
    'wiley': wiley_spider,
    'arxiv': arxiv_spider,
    # 'acm': acm_spider,
    'theiet': theiet_spider
}

# the site with no keywords
ignore_site_pool = ['books.google.com',
                    'journals.aps.org',
                    'www.osapublishing.org',
                    'www.google.com/patents',
                    'iopscience.iop.org',
                    'www.tandfonline.com',
                    'www.researchgate.net',
                    'onlinewww.jpier.org',
                    'scitation.aip.org']
