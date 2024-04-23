import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup

def get_paragraphs_from_url(url):
# Récupère le code source de la page
    response = requests.get(url = url)
    html = response.text
    page = BeautifulSoup(html, 'html.parser')
    my_list = []
    if page.find_all('p') is not None:
        for paragraph in page.find_all('p')[:2]:
            line = paragraph.get_text().replace('\n', '')    
            my_list.append(line)
    return my_list