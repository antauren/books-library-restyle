import os

import requests


def download_book_from_tululu(book_id, ext='txt', allow_redirects=False):
    if ext not in {'txt', 'zip', 'jar'}:
        raise TypeError('File must have ".txt", ".zip" or ".jar" ext.')

    url = 'http://tululu.org/{ext}.php?id={book_id}'.format(book_id=book_id, ext=ext)

    file_name = '{book_id}.{ext}'.format(book_id=book_id, ext=ext)

    book_dir = 'books'
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