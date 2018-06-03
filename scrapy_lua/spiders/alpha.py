# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.shell import inspect_response
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest


class AlphaSpider(scrapy.Spider):
    name = 'hefna_spider'
    allowed_domains = ['ahmedhefnawi.com']
    start_urls = ['https://ahmedhefnawi.com']

    script = """
    function main(splash, args)
        splash:go(splash.args.url)
        splash:wait(0.5)
        local title = splash:evaljs("document.title")
        return {title=title}
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute',
                                args={'lua_source': self.script},
                                cache_args='lua_source')

    def parse(self, response):
        inspect_response(response, self)
        # yield {'test_body': response.body_as_unicode()}


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(AlphaSpider)
    process.start()  # the script will block here until the crawling is finished
