import requests

from bs4 import BeautifulSoup


def get_book_data(book_id):
    url = 'http://tululu.org/b{}/'.format(book_id)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.find('div', id='content').find('h1')

    name, author = get_name_and_author_from_title(h1.text)

    return {'name': name,
            'author': author,
            }


def get_name_and_author_from_title(book_title):
    return book_title.split(' \xa0 :: \xa0 ')
