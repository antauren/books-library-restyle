import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def get_book_data(book_id):
    url = 'http://tululu.org/b{}/'.format(book_id)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.find('div', id='content').find('h1')

    name, author = get_name_and_author_from_title(h1.text)

    div = soup.find('div', class_='bookimage')
    img_src = div.a.img['src']
    img_url = urljoin('http://tululu.org', img_src)

    return {'name': name,
            'author': author,
            'img_url': img_url,
            }


def get_name_and_author_from_title(book_title):
    return book_title.split(' \xa0 :: \xa0 ')
