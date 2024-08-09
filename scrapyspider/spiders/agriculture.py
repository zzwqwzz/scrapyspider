import scrapy
from scrapy import Request
from scrapy.spiders import Spider
from scrapyspider.items import ArticleItem
from scrapyspider.de_weight import de_weight
import copy

class Agriculture(Spider):
    name = 'agriculture'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    }

    def start_requests(self):
        url = 'https://www.agriculture.com/news'
        yield Request(url, callback=self.parse)

    def parse(self, response):
        urls = set(response.xpath("//div[@id='mntl-three-post__inner_1-0']/a/@href").extract())
        tem_url = set(response.xpath("//div[@id='mntl-taxonomysc-article-list-group_1-0']/div/div[1]/a/@href").extract())
        urls = urls.union(tem_url)
        tempurl = copy.deepcopy(urls)
        urls = de_weight(urls, tempurl, self.name)
        for u in urls:
            yield scrapy.Request(url=u, callback=self.detail_parse)

    def detail_parse(self, response):
        url = response.url
        title = response.xpath("//div[@id='agriculture-article-header_1-0']/h1/text()").extract()[0]
        try:
            publish_time = response.xpath("//div[@id='agriculture-article-header_1-0']/div[2]/div[1]/div/div[2]/text()").extract()[0]
        except:
            publish_time = ''
        try:
            publisher = response.xpath("//div[@id='agriculture-article-header_1-0']/div[2]/div[1]/div/div[1]/div/a/text()").extract()[0]
        except:
            publisher = ''
        content = response.xpath("//div[@id='mntl-sc-page_1-0']/p/text()").extract()
        content = '\n'.join(content)

        item = ArticleItem()
        item['url'] = url
        item['site_name'] = self.name
        item['title'] = title
        item['publish_time'] = publish_time
        item['author'] = publisher
        item['content'] = content
        yield item