#coding:utf-8
'''
auto_dump.py：
    用于自动导出备份数据库，并云同步至dropbox
'''
import os,time

def auto_dump_sql(date_str):
    #dump_file_name = date_str + '.sql'
    dump_file_name = 'latest_dump.sql'
    os.system(
        'pg_dump -U gao -f ~/Dropbox/backups/'+ dump_file_name + ' sf_development'
    )
    print('dump sql ok!upload to dropbox...')
    os.system(
        '~/dropbox_uploader.sh upload ~/Dropbox/backups/'+dump_file_name+' backups '
    )
    print('upload sql ok!')


def auto_dump_log():
    os.system(
        '~/dropbox_uploader.sh upload ~/scholar_articles/src/amount_log.txt backups'
    )
    os.system(
        'swift upload visualspider amount_log.txt'
    )#only use in 'src'
    print('upload log ok!')


if __name__ == '__main__':
    auto_dump_log()
    while True:
        date_str = time.strftime("%Y_%m_%d",time.localtime(time.time()))
        auto_dump_sql(date_str)#一天一次
        for i in range(0,24):
            auto_dump_log()#一小时一次
            time.sleep(60*60)

