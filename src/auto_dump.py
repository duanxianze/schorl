#coding:utf-8
'''
auto_dump.py：
    用于自动导出备份数据库，并云同步至dropbox
'''
import os,time

def auto_dump(date_str):
    #dump_file_name = date_str + '.sql'
    dump_file_name = 'latest_dump.sql'
    os.system(
        'pg_dump -U gao -f ~/Dropbox/backups/'+ dump_file_name + ' sf_development'
    )
    print('dump ok!upload to dropbox...')
    os.system(
        './dropbox_uploader.sh upload ~/Dropbox/backups/'+dump_file_name+' backups '
    )
    print('upload ok!')


if __name__ == '__main__':
    #auto_dump('2015_5_23')
    while True:
        date_str = time.strftime("%Y_%m_%d",time.localtime(time.time()))
        auto_dump(date_str)
        time.sleep(60*60*24)

