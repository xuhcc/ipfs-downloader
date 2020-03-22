# IPFS downloader

Sometimes the file which is available via public IPFS gateway is not accessible through p2p network. This can cause issues if you use [IPFS companion](https://github.com/ipfs-shipyard/ipfs-companion).

IPFS downloader is a script that downloads file or directory from public gateway and adds it to your own node.

## Installation

```
pip install -r requirements.txt
```

Then set `IPFS_API` env variable or use `.env` file (see [example](.env.example)).

## Usage

Download from URL:

```
python main.py --url <url>
```

Search for IPFS links in HTML file and download everything:

```
python main.py --html <path/to/file>
```
