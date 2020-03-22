import argparse
import os
import re
import shutil
import tempfile

import bs4
import ipfshttpclient
import requests
from dotenv import load_dotenv

load_dotenv(verbose=True)

IPFS_API = os.getenv('IPFS_API')


def download(url: str, output_dir: str) -> str:
    # Extract IPFS hash
    match = re.match(
        r'(?P<gateway>.+)/ipfs/(?P<hash>[A-Za-z0-9]+)/?(?P<name>[^/]*)',
        url,
    )
    ipfs_gateway = match.group('gateway')
    ipfs_name = match.group('name') or 'default'
    print(f'Downloading {url}...')
    response = requests.get(url)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type')
    if content_type and content_type.startswith('text/html'):
        # It's a directory
        data = bs4.BeautifulSoup(response.text, 'html.parser')
        # Download files recursively
        downloaded = 0
        for link in data.find_all('a'):
            href = link.get('href')
            if not href or '/ipfs/' not in href:
                continue
            child_url = f'{ipfs_gateway}{href}'
            if child_url == url:
                # Index
                continue
            download(child_url, output_dir)
            downloaded += 1

        if downloaded > 0:
            return output_dir
        else:
            return None
    else:
        print(f'Downloaded {len(response.content)} bytes.')
        output_path = os.path.join(output_dir, ipfs_name)
        with open(output_path, 'wb') as downloaded_file:
            downloaded_file.write(response.content)
        return output_path


def process_url(url: str):
    client = ipfshttpclient.connect(IPFS_API)
    output_dir = tempfile.mkdtemp()
    output_path = download(url, output_dir)
    if not output_path:
        print('No files found.')
        return
    print(f'Adding {output_path} to IPFS node...')
    result = client.add(
        output_path,
        recursive=True if output_path == output_dir else False,
        pin=False,
    )
    if isinstance(result, list):
        ipfs_hash = result[-1]['Hash']
    else:
        ipfs_hash = result['Hash']
    print(f'Added as {ipfs_hash}')
    shutil.rmtree(output_dir)
    print('Done.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--html')
    args = parser.parse_args()
    if args.url:
        process_url(args.url)
    elif args.html:
        with open(args.html, 'r') as html_file:
            urls = re.findall(
                r'"([^"]+/ipfs/[A-Za-z0-9]+/?)[^"]*"',
                html_file.read(),
            )
        for url in set(urls):
            process_url(url)


if __name__ == '__main__':
    main()
