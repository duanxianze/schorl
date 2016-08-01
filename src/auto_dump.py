import os,time

def auto_dump(date_str):
	dump_file_name = date_str + '.sql'
	os.system('pg_dump -U postgres -f '+ dump_file_name + ' sf_development')


if __name__ == '__main__':
	auto_dump('2015_5_23')
	'''
	while True:
		date_str = time.strftime("%Y_%m_%d",time.localtime(time.time()))
		auto_dump(date_str)
		time.sleep(60*60*24)
	'''
