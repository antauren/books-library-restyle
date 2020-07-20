import os

import json
import requests
from urllib.parse import urlparse

from tqdm import tqdm
from pathvalidate import sanitize_filename

from tululu_parser import get_book_data
from parse_tululu_category import get_book_ids_by_genre


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

    return file_path


def download_txt(url, filename, folder='books'):
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder,
                             '{}.txt'.format(filename)
                             )

    download_file(url, file_path)

    return file_path


def download_book(book_id):
    book_data = get_book_data(book_id)

    filename = '{}_id{}'.format(book_data['title'], book_id)
    sanitized_filename = sanitize_filename(filename)

    return {'title': book_data['title'],
            'author': book_data['author'],
            'comments': book_data['comments'],
            'genres': book_data['genres'],

            'img_src': download_image(book_data['img_url']),
            'book_path': download_txt(url=book_data['txt_url'], filename=sanitized_filename),
            }


def download_books_by_genre(genre_id, start_page=1, end_page=0):
    book_ids = get_book_ids_by_genre(genre_id, start_page, end_page)

    downloaded_books = []
    for book_id in tqdm(book_ids, desc='download_books'):
        try:
            book = download_book(book_id)
            downloaded_books.append(book)
        except TypeError:
            error = 'The book (id_{}) was not downloaded.'.format(book_id)
            tqdm.write(error)
            continue

    json_filename = '{}.json'.format(genre_id)
    with open(json_filename, 'w', encoding='utf-8') as fd:
        json.dump(downloaded_books, fd, indent=4, ensure_ascii=False)

    return json_filename
