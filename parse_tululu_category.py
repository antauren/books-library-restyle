import requests

import json

from tqdm import tqdm
from bs4 import BeautifulSoup

from tululu import download_book


def get_book_ids_by_genre(genre_id, start_page=1, end_page=0) -> set:
    url = 'http://tululu.org/l{genre_id}/{page_num}/'.format(genre_id=genre_id, page_num=start_page)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_ids = {int(anchor['href'][2: -1]) for anchor in soup.select('.bookimage a')}

    last_page = end_page or int(soup.select('.npage')[-1].text)

    if start_page < last_page:
        book_ids.update(get_book_ids_by_genre(genre_id, start_page=start_page + 1, end_page=end_page))

    return book_ids


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
