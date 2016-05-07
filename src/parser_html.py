from bs4 import BeautifulSoup

class ParseHTML:
    def __init__(self):
        with open('scholar_articles.htm', 'rb') as f:
            self.html = f.read()

        self.soup = BeautifulSoup(self.html, 'lxml')
        self.html_text = self.soup.text

    @property
    def title(self):
        pass

    @property
    def year(self):
        pass

    @property
    def citations_count(self):
        pass

    @property
    def link(self):
        pass

    @property
    def bibtex(self):
        pass

    @property
    def resource_type(self):
        pass

    @property
    def resource_link(self):
        pass

    @property
    def summary(self):
        pass

    @property
    def google_id(self):
        pass
