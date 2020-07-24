import os
import json
from time import sleep

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


def download_books_by_genre(genre_id, start_page=1, end_page=0,
                            skip_imgs=False,
                            skip_txt=False,
                            json_path='',
                            dest_folder='downloads'):
    book_ids = get_book_ids_by_genre(genre_id, start_page, end_page)

    downloaded_books = []

    pbar = tqdm(book_ids, desc='download_books')
    while book_ids:
        book_id = book_ids.pop()
        book_url = 'http://tululu.org/b{}/'.format(book_id)

        try:
            book = download_book(book_id, skip_imgs, skip_txt, dest_folder)
            downloaded_books.append(book)

            tqdm.write('{} OK'.format(book_url))
            pbar.update()

        except (requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError, ConnectionError) as err:
            book_ids.add(book_id)

            seconds = 5
            tqdm.write('The request will be repeated in {} seconds.\n{}'.format(seconds, err))
            sleep(seconds)

        except requests.HTTPError:
            tqdm.write('{} Error'.format(book_url))
            pbar.update()
            continue

    json_folder = json_path or dest_folder
    os.makedirs(json_folder, exist_ok=True)
    json_filename = os.path.join(json_folder, '{}.json'.format(genre_id))
    with open(json_filename, 'w', encoding='utf-8') as fd:
        json.dump(downloaded_books, fd, indent=4, ensure_ascii=False)

    return json_filename


def parse_args():
    parser = argparse.ArgumentParser(
        description='''\
            Данный скрипт скачивает книги определенного жанра с сайта http://tululu.org/.
            
            Жанр по умолчанию - фантастика (genre_id=55).
            Чтобы скачать ВСЕ книги выбранного жанра, нужно указать параметр `--all_books`.
            '''
    )

    fantastic_genre_id = 55

    parser.add_argument('--genre_id', type=int, default=fantastic_genre_id)
    parser.add_argument('--start_page', type=int, default=1)
    parser.add_argument('--end_page', type=int, default=1)

    parser.add_argument('--skip_imgs', action='store_const', const=True)
    parser.add_argument('--skip_txt', action='store_const', const=True)
    parser.add_argument('--all_books', action='store_const', const=True)
    parser.add_argument('--json_path', type=str, default='')
    parser.add_argument('--dest_folder', type=str, default='downloads', help='destination folder')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.start_page > args.end_page:
        raise ValueError('Параметр start_page не может быть больше end_page.')

    start_page = 1 if args.all_books else args.start_page
    end_page = 0 if args.all_books else args.end_page

    json_path = download_books_by_genre(
        args.genre_id,
        start_page,
        end_page,
        args.skip_imgs,
        args.skip_txt,
        json_path=args.json_path,
        dest_folder=args.dest_folder
    )

    tqdm.write('{}'.format(json_path))


if __name__ == '__main__':
    main()
