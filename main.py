import sys
from pathlib import Path
import asyncio
from time import time

from bs4 import BeautifulSoup as BS
import aiohttp
import aiofiles
import aiofiles.os


async def scrape_thread(thread_url, export_path, session):
    num_images = 0

    thread_url_split = thread_url.split('/')
    thread_id = thread_url_split[-1]
    board_id = thread_url_split[-3]

    soup = None

    async with session.get(thread_url) as r:
        if r.status == 200:
            soup = BS(await r.content.read(), "html.parser")
        else:
            print(
                f'{r.status_code} status code from GET request: {r.url}')

    thread_title = soup.find(
        'span', {'class': 'subject'}).string.replace(' ', '-').replace('/', '_slash_').lower()

    thread_folder_path = export_path / \
        f'{board_id}-{thread_id}-{thread_title}'
    Path(thread_folder_path).mkdir(parents=True, exist_ok=True)

    img_urls = [thumb.attrs['href'].replace(
        '//', 'https://') for thumb in soup.find_all('a', {'class': 'fileThumb'})]

    for url in img_urls:
        filepath = thread_folder_path / url.split('/')[-1]
        if await aiofiles.os.path.exists(filepath):
            continue
        async with session.get(url) as r:
            if r.status == 200:
                async with aiofiles.open(filepath, mode='wb') as f:
                    await f.write(await r.content.read())
                    num_images += 1
            else:
                print(f'{r.status_code} status code from GET request: {r.url}')

    return num_images


async def main():
    export_path = Path(
        Path.home() / f'Pictures/.4c/')

    thread_urls = []

    if len(sys.argv) < 2:
        thread_urls = [url for url in input(
            "Thread URL(s): ").split() if url.startswith('http')]
    else:
        thread_urls = [url for url in sys.argv[1:] if url.startswith('http')]

    async with aiohttp.ClientSession() as session:
        thread_coroutines = [scrape_thread(
            url, export_path, session) for url in thread_urls]
        return sum(await asyncio.gather(*thread_coroutines))


if __name__ == '__main__':
    start = time()
    num_images = asyncio.run(main())
    end = time()
    print('TIME: ' + str(end - start))
    print('NUM IMAGES: ' + str(num_images))
