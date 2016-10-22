#coding:utf-8
"""
@file:      get_major_journals.py
@author:    lyn
@contact:   tonylu716@gmail.com
@python:    3.3
@editor:    PyCharm
@create:    2016-09-17 2:20
@description:
        The main entrance of Journal Tasks started with different Major.

        本模块由major关键词出发，首先匹配数据表中的专业范围（包括大类和小类），
        通过该范围来确定其杂志社范围。
        需要注意的是，需要根据专业特性
        （杂志社的分布情况，专业分支交叉情况）来微调参数。
"""

from db_config import REMOTE_CONNS_POOL

class MajorEntrance:
    '''
        本类以专业名（可模糊匹配）为入口，该模块可返回与之相关的杂志条目集合，
        匹配h_index（论文质量）较高，且非跨领域（可选）的杂志社
    '''
    def __init__(self,major_keyword):
        self.cur = REMOTE_CONNS_POOL.new_db_cursor()
        self.major_keyword = major_keyword

    @property
    def possible_areas(self):
        cur = self.cur
        cur.execute(
            "select name,sjr_id from sjr_area \
              WHERE name like '%{}%'".format(self.major_keyword)
        )
        return cur.fetchall()

    @property
    def possible_categories(self):
        cur = self.cur
        possible_areas = self.possible_areas
        if len(possible_areas)==1:
            #假如area已经定位成功，则返回该area下的所有子类
            cur.execute(
                "select name,sjr_id,area_id from sjr_category \
                    WHERE area_id={}".format(possible_areas[0][1])
            )
        else:
            #若area未定位成功，模糊匹配category表
            #area搜索结果数为0，或>1都是失败的情况
            cur.execute(
                "select name,sjr_id,area_id from sjr_category \
                    WHERE name like '%{}%'".format(self.major_keyword)
            )
        return cur.fetchall()

    def get_possible_journals(self,index_by_area=True,index_by_category=True,
            single_area_relation=True,open_access=True,limit=100):
        '''
            注意此处的几个参数，需要根据领域特性微调
            1.假如领域分支较笼统，建议选index_by_area（通过大类找杂志）,反之则用小类找
            2.是否需要非跨领域的杂志社，可选参数single_area_relation
        '''
        if index_by_area:
            print('Generating by Area...')
            journal_dict = journals_of_specific_major(
                possible_db_items = self.possible_areas,
                journals_of_specific_func = journals_of_specific_area,
                tag_info = 'Area',
                single_area_relation = single_area_relation,
                open_access = open_access,
                limit = limit
            )
            print('--------------------------------')
        if index_by_category:
            print('Generating by Category...')
            journal_dict = journals_of_specific_major(
                possible_db_items = self.possible_categories,
                journals_of_specific_func = journals_of_specific_category,
                tag_info = 'Category',
                single_area_relation = single_area_relation,
                open_access = open_access,
                limit = limit
            )
        '''
            journal_dict is like:{
                'major name 1': db_items1,
                'major name 2': db_items2,
             }
        '''
        return journal_dict


    def show_in_cmd(self):
        print('possible_areas:\t\t{}'.format(self.possible_areas))
        print('possible_categories:\t{}'.format(self.possible_categories))



'''
    funcs of major index, below
'''
def categories_of_specific_area(area_sjr_id):
    cur = REMOTE_CONNS_POOL.new_db_cursor()
    cur.execute(
        'select name,sjr_id from sjr_category \
            WHERE area_id={}'.format(area_sjr_id)
    )
    return cur.fetchall()

def journals_of_specific_index(
        index_sjr_id,single_area_relation,
        index_name,open_access,limit=100
):
    if single_area_relation:
        single_area_relation_word = ' area_relation_cot=1 and '
    else:
        single_area_relation_word = ''
    if open_access:
        open_access_word = ' open_access=true and '
    else:
        open_access_word = ''
    cur = REMOTE_CONNS_POOL.new_db_cursor()
    if limit < 0:
        limit = -limit
        desc_word = 'desc'
    else:
        desc_word = ''
    sql =  "select name,sjr_id,site_source,area_relation_cot,\
            category_relation_cot,publisher,volume_links_got from journal \
          WHERE{}{}(site_source like '%lsevier%' or site_source like '%ieee%' or site_source like '%springer%')and\
          is_crawled_all_article=FALSE and \
          sjr_id IN(\
            select journal_id from journal_{} \
            WHERE {}_id={} \
        ) ORDER by h_index {} limit {}".format(
            single_area_relation_word,open_access_word,
            index_name,index_name,index_sjr_id,desc_word,limit
        )
    #print(sql)
    cur.execute(sql)
    return cur.fetchall()

def journals_of_specific_category(category_sjr_id,single_area_relation,open_access):
    #假如多于十个则按h_index排出前十
    return journals_of_specific_index(category_sjr_id,single_area_relation,'category',open_access)

def journals_of_specific_area(area_sjr_id,single_area_relation,open_access):
    return journals_of_specific_index((area_sjr_id,single_area_relation,'area'),open_access)

def journals_of_specific_major(
    possible_db_items,journals_of_specific_func,tag_info,
    single_area_relation = True,open_access = True
):
    journal_dict = {}
    index = 1
    print('\n{} amount:\t{}\nFollwing of them:\n'\
      .format(tag_info,len(possible_db_items)))
    for db_item in possible_db_items:
        item_sjr_id = db_item[1]
        item_name = db_item[0]
        journal_items = journals_of_specific_func(
            item_sjr_id,single_area_relation,open_access)
        journal_dict[item_name] = journal_items
        print('{}.{}({}):'\
            .format(index,item_name,len(journal_items)))
        for item in journal_items:
            print(item)
        index += 1
        print('\n')
    return journal_dict


class PublisherEntrance:
    def __init__(self,publisher_keyword):
        self.publisher_keyword = publisher_keyword

    def get_unfinished_journals(
            self,single_area_relation=True,open_access=True,limit=100,volume_links_got=True):
        journal_filter = ' '
        if limit < 0:
            limit = -limit
            desc_word = 'desc'
        else:
            desc_word = ''
        if single_area_relation:
            journal_filter += ' area_relation_cot=1 and '
        if open_access:
            journal_filter += ' open_access=true and '
        if volume_links_got != 'no limit':
            if volume_links_got:
                journal_filter += ' volume_links_got=true and '
            else:
                journal_filter += ' volume_links_got=false and '
        cur = REMOTE_CONNS_POOL.new_db_cursor()
        sql =  "select name,sjr_id,site_source,area_relation_cot,\
                    category_relation_cot,publisher,volume_links_got from journal \
              WHERE{}is_crawled_all_article=FALSE\
                and ( site_source like '%{}%') order by id {} limit {}"\
            .format(journal_filter,self.publisher_keyword,desc_word,limit)
        #print(sql)
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        return {self.publisher_keyword:data}


if __name__=="__main__":
    x = PublisherEntrance('informa').get_unfinished_journals()
    for y in x:
        print(y)
    '''
    major = MajorEntrance(major_keyword='Science')
    major.show_in_cmd()
    major.get_possible_journals(
        single_area_relation=True,
        index_by_area=False,
        index_by_category=True,
        open_access=True
    )
    '''
    # 非跨领域，且从小类分
    # 因为前期目标是定位学者，杂志社领域精度越细越好
