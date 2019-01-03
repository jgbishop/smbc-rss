import argparse
import feedparser
import json
import os
import pprint
import rfeed
import sys

from bs4 import BeautifulSoup
from contextlib import closing
from datetime import datetime
from requests import get
from requests.exceptions import RequestException


MIN_PYTHON = (3, 6)
VERSION = "0.1.0"


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error(f'Error during requests to {url} : {str(e)}')
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


if sys.version_info < MIN_PYTHON:
    print(f"Python version too old; must use {MIN_PYTHON}")
    sys.exit()

cwd = os.getcwd()
github_url = 'https://github.com/jgbishop/smbc-rss'

parser = argparse.ArgumentParser()
parser.add_argument('--file', default='smbc-config.json')
args = parser.parse_args()

# Load the config file
with open(args.file) as f:
    config = json.load(f)

# Make sure we have everything we expect
errors = []
for x in ('feed_dir', 'feed_url', 'source_feed'):
    if not config.get(x, ""):
        errors.append(f"ERROR: Missing the {x} configuration directive")
    else:
        # Strip trailing slashes from file system paths and URLs
        config[x] = config[x].rstrip('/')

if errors:
    sys.exit("\n".join(errors))

# Create the feed directory
feed_dir = config.get('feed_dir')
if not feed_dir.startswith('/'):
    feed_dir = os.path.join(cwd, feed_dir)

try:
    os.makedirs(feed_dir, exist_ok=True)
except OSError as e:
    sys.exit(f"Failed to create {feed_dir}: {str(e)}")

in_feed = feedparser.parse(config.get('source_feed'))
item_list = []

limit = 7
for entry in in_feed.entries:
    if limit == 0:
        break

    link = entry.link
    raw_html = simple_get(link)
    html = BeautifulSoup(raw_html, 'lxml')

    page_title = html.title.string

    comic = html.select_one("#cc-comic")
    title = comic['title']
    comic_img = comic['src']

    votey = html.select_one('#aftercomic > img')
    votey_img = votey['src']

    clines = [
        f'<p><img src="{comic_img}" alt="Main comic"></p>',
        f'<p>Hover Text: {title}</p>',
        f'<p><img src="{votey_img}" alt="Extra joke"></p>',
    ]

    time_raw = entry.published
    pub_time = datetime.strptime(time_raw, '%a, %d %b %Y %H:%M:%S %z')

    print(f"\nLink: {link}")
    print(f"  - Comic: {comic_img}")
    print(f"  - Title: {title}")
    print(f"  - Votey: {votey_img}")

    item = rfeed.Item(
        title=page_title,
        link=link,
        description='\n'.join(clines),
        guid=rfeed.Guid(link),
        pubDate=pub_time,
    )
    item_list.append(item)

    limit -= 1

out_feed = rfeed.Feed(
    title="Saturday Morning Breakfast Cereal",
    link='https://www.smbc-comics.com/',
    description="RSS feed for Saturday Morning Breakfast Cereal",
    language="en-US",
    lastBuildDate=datetime.now(),
    items=item_list,
    generator=f"smbc-rss.py {github_url}"
)

out_feed_path = os.path.join(config.get('feed_dir'), "smbc-rss.xml")
with open(out_feed_path, 'w') as out_feed_file:
    out_feed_file.write(out_feed.rss())
