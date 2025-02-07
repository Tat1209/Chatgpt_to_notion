from bs4 import BeautifulSoup

class NotionTrans:
    def __init__(self, html):
        self.html_body = BeautifulSoup(html, "lxml").body
        