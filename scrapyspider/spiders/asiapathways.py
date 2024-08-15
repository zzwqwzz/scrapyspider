import time
from newspaper import Article
from scrapy import Request
from scrapy.spiders import Spider
from scrapyspider.items import ArticleItem
from scrapyspider.utils import save, de_weight
import copy
import re

class Asiapathways(Spider):
    name = 'asiapathways'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }
    data = time.strftime('%Y%m%d', time.localtime(time.time()))

    def start_requests(self):
        url = 'https://www.asiapathways-adbi.org/'
        yield Request(url=url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        urls = set(response.xpath("//div[@id='main']/div/a/@href").extract())
        tempurl = copy.deepcopy(urls)
        for u in tempurl:
            result = re.match("^.*/page/.*/$", u)
            if result != None:
                urls.remove(u)
        urls = de_weight(urls, tempurl, self.name)
        for u in urls:
            yield Request(url=u, callback=self.detail_parse)

    def detail_parse(self, response):
        url = response.url
        art = Article(url)
        art.download()
        art.parse()
        title = art.title
        publish_time = art.publish_date
        author = ','.join(response.xpath("//a[@rel='author']/text()").extract())
        text = art.text.split('\n')
        temptext = copy.deepcopy(text)
        for e in temptext:
            if e == '':
                text.remove('')
        content = '\n'.join(text)

        save(self.name, self.data, art.html, title)

        item = ArticleItem()
        item['url'] = url
        item['site_name'] = self.name
        item['title'] = title
        item['publish_time'] = publish_time
        item['author'] = author
        item['content'] = content
        time.sleep(1)
        yield item