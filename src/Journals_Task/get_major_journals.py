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
            需要注意的是，需要根据专业特性来微调参数。
"""

from src.db_config import new_db_cursor

class MajorEntrance:
    '''
        本类以专业名（可模糊匹配）为入口，该模块可返回与之相关的杂志条目集合，
        匹配h_index（论文质量）较高，且非跨领域（可选）的杂志社
    '''
    def __init__(self,major_keyword):
        self.cur = new_db_cursor()
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
        cur.execute(
            "select name,sjr_id,area_id from sjr_category \
                WHERE name like '%{}%'".format(self.major_keyword)
        )
        return cur.fetchall()

    def get_possible_journals(self,index_by_area=True,
            index_by_category=True,single_area_relation=True):
        '''
            注意此处的几个参数，需要根据领域特性微调
            1.假如领域分支较多，建议选index_by_area（通过大类找杂志）,反之则用小类找
            2.是否需要非跨领域的杂志社，可选参数single_area_relation
        '''
        if index_by_area:
            print('Generating by Area...')
            journal_dict = journals_of_specific_major(
                possible_db_items = self.possible_areas,
                journals_of_specific_func = journals_of_specific_area,
                tag_info = 'Area',
                single_area_relation = single_area_relation
            )
            print('--------------------------------')
        if index_by_category:
            print('Generating by Category...')
            journal_dict = journals_of_specific_major(
                possible_db_items = self.possible_categories,
                journals_of_specific_func = journals_of_specific_category,
                tag_info = 'Category',
                single_area_relation = single_area_relation
            )
        '''
            journal_dict is like:{
                'major name 1':{'length':n,'db_items':[x,y,z]},
                'major name 2':{'length':n,'db_items':[w,m,n]},
             }
             建议迭代时用for key in journal_dict.keys():   pass
        '''
        return journal_dict


    def show_in_cmd(self):
        print('possible_areas:\t\t{}'.format(self.possible_areas))
        print('possible_categories:\t{}'.format(self.possible_categories))



'''
    funcs of major index, below
'''
def categories_of_specific_area(area_sjr_id):
    cur = new_db_cursor()
    cur.execute(
        'select name,sjr_id from sjr_category \
            WHERE area_id={}'.format(area_sjr_id)
    )
    return cur.fetchall()

def journals_of_specific_category(category_sjr_id,single_area_relation):
    #假如多于十个则按h_index排出前十
    if single_area_relation:
        single_area_relation_word = 'and area_relation_cot=1'
    else:
        single_area_relation_word = ''
    cur = new_db_cursor()
    cur.execute(
        'select name,sjr_id,h_index,site_source from journal \
          WHERE sjr_id IN(\
            select journal_id from journal_category \
            WHERE site_source is not null and category_id={}\
        ) {} ORDER by h_index desc limit 10'.format(
            category_sjr_id,single_area_relation_word
        )
    )
    return cur.fetchall()

def journals_of_specific_area(area_sjr_id,single_area_relation):
    if single_area_relation:
        single_area_relation_word = 'and area_relation_cot=1'
    else:
        single_area_relation_word = ''
    cur = new_db_cursor()
    cur.execute(
        'select name,sjr_id,h_index,site_source from journal \
          WHERE sjr_id IN(\
            select journal_id from journal_area \
            WHERE site_source is not null and area_id={}\
        ) {} ORDER by h_index desc limit 50'.format(
            area_sjr_id,single_area_relation_word
        )
    )
    return cur.fetchall()

def journals_of_specific_major(
    possible_db_items,journals_of_specific_func,tag_info,
    single_area_relation = True
):
    journal_dict = {}
    for db_item in possible_db_items:
        item_sjr_id = db_item[1]
        item_name = db_item[0]
        journal_items = journals_of_specific_func(item_sjr_id,single_area_relation)
        journal_dict[item_name] = {
            'db_items':journal_items,
            'length':len(journal_items)
        }
    print('\n{} amount:\t{}\nFollwing of them:\n'\
          .format(tag_info,len(possible_db_items)))
    index = 1
    for key in (journal_dict.keys()):
        key_journals = journal_dict[key]
        print('{}.{}({}):'\
            .format(index,key,key_journals['length']))
        for item in key_journals['db_items']:
            print(item)
        index += 1
        print('\n')
    return journal_dict



if __name__=="__main__":
    major = MajorEntrance(major_keyword='Computer')
    major.show_in_cmd()
    major.get_possible_journals(
        single_area_relation=True,
        index_by_area=False,
        index_by_category=True
    )
    #非跨领域，且从小类分