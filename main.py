import sys
from pathlib import Path

from bs4 import BeautifulSoup as BS
import requests
from time import time


def main():
    export_path = Path(Path.home() / 'Pictures/.4c/__TEST__SYNC')

    num_images = 0

    thread_urls = []

    if len(sys.argv) < 2:
        thread_urls = [url for url in input(
            "Thread URL(s): ").split() if url.startswith('http')]
    else:
        thread_urls = [url for url in sys.argv[1:] if url.startswith('http')]

    for thread_url in thread_urls:
        thread_url_split = thread_url.split('/')
        thread_id = thread_url_split[-1]
        board_id = thread_url_split[-3]

        soup = None

        response = requests.get(thread_url)
        if response.status_code == 200:
            soup = BS(response.text, "html.parser")
        else:
            print(f'{response.status_code} status code from GET request: {res.url}')

        thread_title = soup.find(
            'span', {'class': 'subject'}).string.replace(' ', '-').replace('/', '_slash_').lower()

        thread_folder_path = export_path / \
            f'{board_id}-{thread_id}-{thread_title}'
        Path(thread_folder_path).mkdir(parents=True, exist_ok=True)

        img_urls = [thumb.attrs['href'].replace(
            '//', 'https://') for thumb in soup.find_all('a', {'class': 'fileThumb'})]

        for url in img_urls:
            filepath = thread_folder_path / url.split('/')[-1]
            if filepath.exists():
                continue

            r = requests.get(url)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                    num_images += 1
            else:
                print(f'{r.status_code} status code from GET request: {r.url}')

    return num_images


if __name__ == '__main__':
    start = time()
    num_images = main()
    end = time()
    print('TIME: ' + str(end - start))
    print('NUM IMAGES: ' + str(num_images))
