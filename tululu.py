import os

import requests
from urllib.parse import urlparse

from pathvalidate import sanitize_filename

from tululu_parser import get_book_data


def download_book_from_tululu(book_id, ext='txt', allow_redirects=False, book_dir='books'):
    book_dir = sanitize_filename(book_dir)

    if ext not in {'txt', 'zip', 'jar'}:
        raise TypeError('File must have ".txt", ".zip" or ".jar" ext.')

    url = 'http://tululu.org/{ext}.php?id={book_id}'.format(book_id=book_id, ext=ext)

    try:
        book = get_book_data(book_id)
        name = book['name']

        book_name = '{}_id{}'.format(name, book_id)
    except AttributeError:
        book_name = book_id

    file_name = '{book_name}.{ext}'.format(book_name=sanitize_filename(book_name), ext=ext)

    os.makedirs(book_dir, exist_ok=True)
    file_path = os.path.join(book_dir, file_name)

    download_file(url, file_path, allow_redirects)


def download_file(url, file_path='', allow_redirects=False):
    if not file_path:
        raise NameError('File must have name.')

    response = requests.get(url, allow_redirects=allow_redirects)
    response.raise_for_status()

    if response.status_code != 200:
        raise TypeError('URL {} is empty.'.format(url))

    with open(file_path, 'wb') as fd:
        fd.write(response.content)


def download_image(url, folder='images'):
    os.makedirs(folder, exist_ok=True)

    path = urlparse(url).path
    _, file_name = os.path.split(path)
    file_path = os.path.join(folder, file_name)

    if file_name == 'nopic.gif' and os.path.exists(file_path) and os.path.isfile(file_path):
        pass
    else:
        download_file(url, file_path)
