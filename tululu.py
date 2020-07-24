import os

import requests
from urllib.parse import urlparse

from pathvalidate import sanitize_filename

from tululu_parser import get_book_data


def download_file(url, file_path='', allow_redirects=False):
    if not file_path:
        raise NameError('File must have name.')

    response = requests.get(url, allow_redirects=allow_redirects)
    raise_for_status(response)

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


def download_book(book_id, skip_imgs=False, skip_txt=False, dest_folder='downloads'):
    book_data = get_book_data(book_id)

    filename = '{}_id{}'.format(book_data['title'], book_id)
    sanitized_filename = sanitize_filename(filename)

    img_dir = os.path.join(dest_folder, 'images')
    book_dir = os.path.join(dest_folder, 'books')

    img_src = download_image(book_data['img_url'], folder=img_dir) if not skip_imgs else None
    book_path = download_txt(url=book_data['txt_url'], folder=book_dir,
                             filename=sanitized_filename) if not skip_txt else None

    return {'title': book_data['title'],
            'author': book_data['author'],
            'comments': book_data['comments'],
            'genres': book_data['genres'],

            'img_src': os.path.join(dest_folder, img_src),
            'book_path': os.path.join(dest_folder, book_path),
            }


def raise_for_status(response):
    response.raise_for_status()

    if response.status_code != 200:
        raise requests.HTTPError(
            'Status code is {} (200 required).'.format(response.status_code)
        )
