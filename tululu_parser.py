import requests
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def get_book_data(book_id, hostname='http://tululu.org'):
    url = '{hostname}/b{book_id}/'.format(hostname=hostname, book_id=book_id)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.select_one('#content h1')
    title, author = get_title_and_author_from_header(h1.text)

    img_src = soup.select_one('.bookimage a img')['src']
    img_url = urljoin(hostname, img_src)

    comments = [comment.text for comment in soup.select('.texts .black')]
    genres = [anchor.text for anchor in soup.find(text='Жанр книги:').parent.findNextSiblings('a')]

    txt_url = '{hostname}/txt.php?id={book_id}'.format(hostname=hostname, book_id=book_id)

    return {'title': title,
            'author': author,
            'img_url': img_url,
            'comments': comments,
            'genres': genres,
            'txt_url': txt_url,
            }


def get_title_and_author_from_header(text):
    return text.split(' \xa0 :: \xa0 ')
