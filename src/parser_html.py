from bs4 import BeautifulSoup

class ParseHTML:
    def __init__(self):
        with open('scholar_articles.htm', 'rb') as f:
            self.html = f.read()

        self.soup = BeautifulSoup(self.html, 'lxml')
        self.html_text = self.soup.text

    def sections(self):
        sections = self.soup.select('.gs_r')
        return sections

    def title(self, sec):
        title = sec.select('.gs_rt > a')
        return title

    def year(self, sec):
        pass

    def citations_count(self, sec):
        pass

    def link(self, sec):
        pass

    def bibtex(self, sec):
        pass

    def resource_type(self, sec):
        pass

    def resource_link(self, sec):
        pass

    def summary(self, sec):
        pass

    def google_id(self, sec):
        pass

p = ParseHTML()
for sec in p.sections():
    print(p.title(sec))
    print("===")
