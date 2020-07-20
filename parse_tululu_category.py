import json

import argparse
import requests
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


def download_books_by_genre(genre_id, start_page=1, end_page=0, skip_imgs=False, skip_txt=False):
    book_ids = get_book_ids_by_genre(genre_id, start_page, end_page)

    downloaded_books = []
    for book_id in tqdm(book_ids, desc='download_books'):

        book_url = 'http://tululu.org/b{}/'.format(book_id)

        try:
            book = download_book(book_id, skip_imgs, skip_txt)
            downloaded_books.append(book)

            tqdm.write('{} OK'.format(book_url))
        except TypeError:
            tqdm.write('{} Error'.format(book_url))
            continue

    json_filename = '{}.json'.format(genre_id)
    with open(json_filename, 'w', encoding='utf-8') as fd:
        json.dump(downloaded_books, fd, indent=4, ensure_ascii=False)

    return json_filename


def parse_args():
    parser = argparse.ArgumentParser(
        description='''\
            Данный скрипт скачивает книги определенного жанра с сайта http://tululu.org/.
            
            Жанр по умолчанию - фантастика (genre_id=55).
            Чтобы скачать ВСЕ книги выбранного жанра, нужно указать параметр `--end_page 0`.
            '''
    )

    fantastic_genre_id = 55

    parser.add_argument('--genre_id', type=int, default=fantastic_genre_id)
    parser.add_argument('--start_page', type=int, default=1)
    parser.add_argument('--end_page', type=int, default=1)

    parser.add_argument('--skip_imgs', action='store_const', const=True)
    parser.add_argument('--skip_txt', action='store_const', const=True)

    return parser.parse_args()


def main():
    args = parse_args()

    json_path = download_books_by_genre(args.genre_id, args.start_page, args.end_page, args.skip_imgs, args.skip_txt)

    print(json_path)


if __name__ == '__main__':
    main()
