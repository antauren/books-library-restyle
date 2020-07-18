import requests

from bs4 import BeautifulSoup


def get_book_ids_by_genre(genre_id, start_page=1, end_page=0) -> set:
    url = 'http://tululu.org/l{genre_id}/{page_num}/'.format(genre_id=genre_id, page_num=start_page)

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    book_ids = {int(anchor['href'][2: -1]) for anchor in soup.select('.bookimage a')}

    last_page = end_page or int(soup.find_all('a', class_='npage')[-1].text)

    if start_page < last_page:
        book_ids.update(get_book_ids_by_genre(genre_id, start_page=start_page + 1, end_page=end_page))

    return book_ids
