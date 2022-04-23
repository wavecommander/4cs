import sys
from pathlib import Path

from bs4 import BeautifulSoup as BS
import requests


def main():
    export_path = Path(Path.home() / 'Pictures/.4c/')

    thread_url = ''

    if len(sys.argv) < 2:
        thread_url = input("Thread URL: ")
    elif sys.argv[1].startswith('http'):
        thread_url = sys.argv[1]
    elif sys.argv[-1].startswith('http'):
        thread_url = sys.argv[-1]

    thread_url_split = thread_url.split('/')
    thread_id = thread_url_split[-1]
    board_id = thread_url_split[-3]

    soup = {}

    response = requests.get(thread_url)
    if response.status_code == 200:
        soup = BS(response.text, "html.parser")
    else:
        print(response.url)
        print(response.status_code)

    thread_title = soup.find(
        'span', {'class': 'subject'}).string.replace(' ', '-').lower()

    thread_folder_path = export_path / \
        f'{board_id}-{thread_id}-{thread_title}'
    Path(thread_folder_path).mkdir(parents=True, exist_ok=True)

    img_urls = [url.attrs['href'].replace(
        '//', 'https://') for url in soup.find_all('a', {'class': 'fileThumb'})]

    for url in img_urls:
        filepath = thread_folder_path / url.split('/')[-1]
        if filepath.exists():
            continue
        r = requests.get(url)
        with open(filepath, 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    main()
