#coding:utf-8
"""
@file:      WileyParser
@author:	xiao t
@date:		2016-10-22
@description:
            nope
"""
import sys,os
up_level_N = 1
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
root_dir = SCRIPT_DIR
for i in range(up_level_N):
    root_dir = os.path.normpath(os.path.join(root_dir, '..'))
sys.path.append(root_dir)

from journal_parser.JournalArticle import JournalArticle
from bs4 import BeautifulSoup
from crawl_tools.decorators import except_pass
EP_METHOD = lambda func:except_pass(func,'WileyArticle')
import re

class WileyAllItemsPageParser:
	'''
		sample_url:	http://onlinelibrary.wiley.com/doi/10.1002/(SICI)1096-987X(199812)19:16%3C%3E1.0.CO;2-O/issuetoc
	'''
	def __init__(self,html_source=None,from_web=True):
		if not from_web:
			with open('Wiley.html','rb') as f:
				html_source = f.read()
		self.soup = BeautifulSoup(html_source,'lxml')

	@property
	def sections(self):
		return self.soup.select('.articles > li')

	@property
	def volume_year(self):
		return int(self.soup.select_one('.noMargin').text.split(' ')[-1])


class WileyArticle(JournalArticle):
	def __init__(self,sec,JournalObj,volume_db_id,year):
		self.sec = sec
		JournalArticle.__init__(self,JournalObj,volume_db_id)
		self.year = year
		self.generate_all_method()

	@EP_METHOD
	def generate_title(self):
		self.title = self.sec.select_one('.tocArticle > a').text.split(' (page')[0]

	@EP_METHOD
	def generate_pdf_temp_url(self):
		self.sec.select_one('.readcubeEpdfLink')['href']
		self.generate_id_by_journal()
		if self.id_by_journal != None:
			self.pdf_temp_url = \
				'http://onlinelibrary.wiley.com/doi/{}/pdf'.format(self.id_by_journal)

	@EP_METHOD
	def generate_link(self):
		self.link = 'http://onlinelibrary.wiley.com' + self.sec.select_one('.tocArticle > a')['href']

	@EP_METHOD
	def generate_id_by_journal(self):
		try:
			self.id_by_journal = self.sec.select('.tocArticle > p')[1].text.split('DOI: ')[-1]
		except:
			self.id_by_journal = self.sec.select('.tocArticle > p')[0].text.split('DOI: ')[-1]

	@EP_METHOD
	def generate_authors(self):
		info = self.sec.select('.tocArticle > p')[0].text
		if 'DOI' in info:
			return
		self.authors = re.split(', | and ',info)


if __name__=="__main__":
	from Journals_Task.JournalClass import Journal
	j = Journal()
	parser = WileyAllItemsPageParser(
		from_web=False
	)
	for sec in parser.sections:
		WileyArticle(sec,j,2,parser.volume_year).show_in_cmd()