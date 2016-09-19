# coding:utf-8
from bs4 import BeautifulSoup as bs
import re

'''
@author: panda0
@description: some spiders crawling keywords from journals
'''


def cqvip_spider(soup):
    # ignore cqvip
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

    return(str(dict)), 'Acquired' if len(dict) > 0 else None, 'Keywords not found'


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


def acm_spider(driver):
    # selenium
    pass


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


def spie_spider(driver):
    # selenium
    pass


def nfona_spider(soup):
    keywords_locate = None
    block_keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(
            class_='tab-pane keyword_list first active ')[0].find_all('a')
    except:
        pass
    try:
        block_keywords_locate = soup.find_all(
            class_='tab-pane all_keyword_list')[0].find_all('a')
    except:
        pass
    if keywords_locate:
        for a in keywords_locate:
            keywords = keywords + a.get_text() + ', '
    if block_keywords_locate:
        for a in block_keywords_locate:
            keywords = keywords + a.get_text() + ', '
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def dbpia_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all()
        for item in keywords_locate:
            for each in item.find_all('a'):
                keywords = keywords + each.get_text() + ','
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def oai_spider(soup):
    descriptors_locate = None
    subjects_locate = None
    descriptors = ''
    subjects = ''
    for p_label in soup.find_all('p'):
        if re.search('Descriptors', str(p_label)):
            descriptors_locate = p_label
        elif re.search('Subject', str(p_label)):
            subjects_locate = p_label
        else:
            pass
    dict = {}
    if descriptors_locate:
        # .replace(',   ', ', ').split('Descriptors :    ')[-1]
        descriptors = descriptors_locate.get_text().strip().split(
            'Descriptors :    ')[-1].replace('\xa0', '').replace(',   ', ', ')
        dict['descriptors'] = descriptors
    if subjects_locate:
        subjects = subjects_locate.get_text().strip().split(
            'Subject Categories  : ')[-1].replace('\xa0', '').replace('       ', ', ')
        dict['subjects'] = subjects
    return(str(dict)), 'Acquired' if len(dict) > 0 else None, 'Keywords not found'


def ingentaconnect_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        for p_label in soup.find_all(id='info')[0].find_all('p'):
            if 'eyword' in p_label.find('strong').get_text():
                keywords_locate = p_label.find_all('a')
                for a_label in keywords_locate:
                    keywords = keywords + a_label.get_text() + ', '
    except:
        pass
    print(keywords)
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def ieice_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.select('a[href^="keyword.php?kword="]')
    except:
        pass
    for a_label in keywords_locate:
        keywords = keywords + a_label.get_text() + ', '
    print(keywords)
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def ncbi_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(class_='kwd-text')
    except:
        pass
    if keywords_locate:
        keywords = keywords_locate[0].get_text().replace(', ', ', ')
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def lww_spider(soup):
    p_label = None
    keywords = ''
    try:
        for p_label in soup.find_all(class_='ej-box-02-body')[0].find_all('p'):
            if 'eyword' in p_label.find('strong').get_text():
                keywords = p_label.get_text().split(
                    'Keywords\r\n')[-1].strip().replace(', ', ', ')
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def cambridge_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(
            class_='button-group inline clearfix')[0].find_all(class_='button small radius grey')
        for a_label in keywords_locate:
            print(a_label.get_text())
            keywords = keywords + a_label.get_text() + ', '
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def harvard_spider(soup):
    haha_locate = None
    keywords = ''
    try:
        haha_locate = soup.find_all('tr')
        for tr_label in haha_locate:
            if 'eyword' in str(tr_label.find('td').find('b')):
                keywords_locate = tr_label.find_all('td')[-1]
                keywords = keywords_locate.get_text()
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


def plos_spider(soup):
    keywords_locate = None
    keywords = ''
    try:
        keywords_locate = soup.find_all(id='subjectList')[0].find_all('li')
        for li_label in keywords_locate:
            words = li_label.find_all('a', class_='taxo-term')[0].get_text()
            keywords = keywords + words + ', '
    except:
        pass
    if keywords:
        return keywords, 'Acquired'
    else:
        return None, 'Keywords not found'


# a dict mapping sites and spiders
spider_pool = {
    # 'cqvip': cqvip_spider,
    'pubs.acs': acs_spider,
    'cnki.com': cnki_spider,
    'sciencedirect': sciencedirect_spider,
    'springer': springer_spider,
    'wiley': wiley_spider,
    'arxiv': arxiv_spider,
    # 'acm': acm_spider,
    'theiet': theiet_spider,
    # 'spiedigitallibrary': spie_spider,
    'nfona.pl': nfona_spider,
    # 'dbpia.co.kr': dbpia_spider,
    'oai.dtic.mil': oai_spider,
    'ingentaconnect': ingentaconnect_spider,
    'ieice.or': ieice_spider,
    'ncbi.nlm.nih': ncbi_spider,
    'journals.lww.com': lww_spider,
    'www.cambridge.org': cambridge_spider,
    'harvard.edu': harvard_spider,
    'journals.plos.org': plos_spider
}

selenium_spider_pool = {
    'proceedings.spiedigitallibrary.org': spie_spider,
    'acm': acm_spider

}


# the site with no keywords
ignore_site_pool = [
    'books.google.com',
    'journals.aps.org',
    'www.osapublishing.org',
    'www.google.com/patents',
    'iopscience.iop.org',
    'www.tandfonline.com',
    'www.researchgate.net',
    'onlinewww.jpier.org',
    'scitation.aip.org',
    'citeseerx.ist.psu.edu',
    'www.nature.com',
    'www.edatop.com',
    'cqvip',
    'pubs.acs.org',
    # 'journals.lww.com',
    'proquest.com',
    'www.pnas.org'
]
