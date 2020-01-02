import store as store_lib
import score as score_lib
import aiohttp
import asyncio
import task_queue
from enum import Enum
from lxml import etree, html
import html_extractor
import sys


class PathType(Enum):
    OPML = 1
    RSS = 2
    HTML = 3


class Crawler(object):
    ''' A class to crawl opml, rss and html files.

    Attributes
    ----------
    _store : Store
        The store to save crawled result.
    _score : Score
        A calculator to calculate the score for a document.
    _session : aiohttp.ClientSession
        aiohttp's client session to make network requests.
    _queue : TaskQueue
        A task queue to execute all crawl tasks asynchronously.
        Each crawl task only crawls one opml/rss/html file
    _visited_url : set
        A set to store visited url so that no duplicate url would be crawled.
    _max_html_recur_level: int
        Max depth of html link which could be crawled.
        We crawl html recursively by traversing all links in each html doc in BFS order.
        To save time for testing, we limit the BFS depth to this int.
    '''

    def __init__(self, store, score, session, queue, max_html_recur_level):
        self._store = store
        self._score = score
        self._session = session
        self._queue = queue
        self._visited_url = set()
        self._max_html_recur_level = max_html_recur_level

    async def crawl(self, path, path_type, title='', html_recur_level=0):
        if path in self._visited_url:
            print('path %s visited' % path)
            return
        self._visited_url.add(path)
        if path_type is PathType.OPML:
            await self._crawl_opml(path)
        elif path_type is PathType.RSS:
            await self._crawl_rss(path)
        else:
            await self._crawl_html(path, title, html_recur_level)

    async def _crawl_opml(self, path):
        if not self._is_valid_opml_path(path):
            return
        tree = etree.parse(path)
        root = tree.getroot()
        rss_feeds = root.findall('.//outline[@type="rss"]')
        for feed in rss_feeds:
            if 'xmlUrl' in feed.attrib:
                self._queue.add_task(
                    self.crawl(
                        feed.attrib.get('xmlUrl'),
                        PathType.RSS))

    async def _crawl_rss(self, url):
        if not self._is_valid_rss_path(url):
            return
        print('crawl rss %s' % url)
        async with self._session.get(url) as response:
            if response.status >= 400:
                print('Error: Fail to fetch rss %s' % url)
                return
            if response.content_type != 'text/xml':
                print(
                    'Error: Bad rss type. Actual content type %s' %
                    response.content_type)
                return

            rss_doc = etree.fromstring(await self._get_response_text_encoded(response))
            if rss_doc.tag == 'rss':
                rss_root = rss_doc
            else:
                rss_root = rss_doc.find('.//rss')

            if rss_root.get('version') != '2.0':
                print(
                    'Error: rss with invalid version. url = %s; version = %s' %
                    (url, rss_root.attrib.get('version')))
                return
            rss_items = rss_root.findall(".//item")
            for rss_item in rss_items:
                title = rss_item.find('title')
                if title is None:
                    print('Error: rss item with no title')
                    continue
                title = title.text
                link = rss_item.find('link')
                if link is None:
                    print('Error: rss item with no link')
                    continue
                link = link.text
                self._queue.add_task(self.crawl(link, PathType.HTML, title))

    async def _crawl_html(self, url, title, html_recur_level):
        if html_recur_level >= self._max_html_recur_level:
            return
        if not self._is_valid_html_path(url):
            return
        print('crawl html %s' % url)
        async with self._session.get(url) as response:
            if response.status >= 400:
                print('Error: Fail to fetch html %s' % url)
                return

            if response.content_type != 'text/html':
                print(
                    'Error: Bad html type. Actual content type %s' %
                    response.content_type)
                return

            html_doc = html.fromstring(await self._get_response_text_encoded(response))
            extractor = html_extractor.get_extractor(url, html_doc)
            text_content = extractor.extract_text()
            score = self._score.calculate_score(text_content)
            if not title:
                title = extractor.extract_title()
            self._store.save(title, url, score)
            for link in extractor.extract_same_origin_links():
                self._queue.add_task(
                    self.crawl(
                        link.get('url'),
                        PathType.HTML,
                        link.get('title'),
                        html_recur_level + 1))

    async def _get_response_text_encoded(self, response):
        return (await response.text()).encode(response.get_encoding())

    def _is_valid_opml_path(self, path):
        return path.endswith('.opml')

    def _is_valid_rss_path(self, url):
        # TODO implement the validator
        return url != ''

    def _is_valid_html_path(self, url):
        # TODO implement the validator
        return url != ''


async def main(opml, html_recur_level):
    store = store_lib.HtmlStore()
    score = score_lib.WordEntropyScore()
    queue = task_queue.TaskQueue(10)
    session = aiohttp.ClientSession()
    crawler = Crawler(store, score, session, queue, html_recur_level)
    queue.add_task(crawler.crawl(opml, PathType.OPML))
    await queue.wait_till_finish()
    await session.close()
    store.flush()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1], int(sys.argv[2])))
