import requests

from bs4 import BeautifulSoup


def get_book_ids_by_genre(genre_id, start_page=1, end_page=0) -> set:
    url = 'http://tululu.org/l{genre_id}/{page_num}/'.format(genre_id=genre_id, page_num=start_page)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_tables = soup.find_all('table', class_='d_book')

    book_ids = set()
    for table in book_tables:
        book_title = table.find_all('tr')[1]
        book_href = book_title.td.a['href']
        book_id = int(book_href[2: -1])

        book_ids.add(book_id)

    last_page = end_page or int(soup.find_all('a', class_='npage')[-1].text)

    if start_page < last_page:
        book_ids.update(get_book_ids_by_genre(genre_id, start_page=start_page + 1, end_page=end_page))

    return book_ids
