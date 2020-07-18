import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def get_book_data(book_id):
    url = 'http://tululu.org/b{}/'.format(book_id)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.select_one('#content h1')

    name, author = get_name_and_author_from_title(h1.text)

    img_src = soup.select_one('.bookimage a img')['src']
    img_url = urljoin('http://tululu.org', img_src)

    comments = [comment.text for comment in soup.select('.texts .black')]
    genres = [anchor.text for anchor in soup.find(text='Жанр книги:').parent.findNextSiblings('a')]

    return {'name': name,
            'author': author,
            'img_url': img_url,
            'comments': comments,
            'genres': genres,
            }


def get_name_and_author_from_title(book_title):
    return book_title.split(' \xa0 :: \xa0 ')
