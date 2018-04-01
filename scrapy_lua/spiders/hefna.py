# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.shell import inspect_response
from scrapy.crawler import CrawlerProcess
from scrapy_splash import SplashRequest



class HefnaSpiderSpider(scrapy.Spider):
    name = 'hefna_spider'
    allowed_domains = ['kiliim.com']
    start_urls = ['https://kiliim.com/shop']

    script_main = """
            function main(splash)
                splash:init_cookies(splash.args.cookies)
                assert(splash:go{
                    splash.args.url,
                    headers=splash.args.headers,
                    http_method=splash.args.http_method,
                    body=splash.args.body,
                })
                splash:wait(0.5)
                local currency = splash:evaljs('document.querySelectorAll("span.woocommerce-Price-currencySymbol")[0].innerHTML')
                if currency ~= "EGP" then
                    splash:go('https://kiliim.com/product/blue-nile-cushion/')
                    local button = splash:select('button.single_add_to_cart_button')
                    button:mouse_click()
                    splash:wait(3.5)
                    splash:go('https://kiliim.com/cart/')
                    splash:wait(3.5)
                    splash:go('https://kiliim.com/checkout/')
                    splash:wait(1.5)
                    local select_go = splash:select('#s2id_billing_country')
                    select_go:mouse_click()
                    local country = splash:select('#s2id_autogen1_search')
                    country:send_text("Egypt")
                    country:send_keys("<Return>")
                    assert(splash:go{splash.args.url})
                end
                splash:wait(0.5)
                local entries = splash:history()
                local last_response = entries[#entries].response
                return {
                    url = splash:url(),
                    headers = last_response.headers,
                    http_status = last_response.status,
                    cookies = splash:get_cookies(),
                    html = splash:html(),
                }
            end
            """

    script = """
            function main(splash)
                splash:go('https://kiliim.com/product/blue-nile-cushion/')
                local button = splash:select('button.single_add_to_cart_button')
                button:mouse_click()
                splash:go('https://kiliim.com/checkout/')
                splash:wait(1.5)
                local select_input = splash:select('#s2id_billing_country')
                select_input:mouse_click()
                local country = splash:select('input[id=s2id_autogen1_search]')
                country:send_text("France")
                country:send_keys("<Return>")
                splash:wait(0.5)
                splash:go('https://kiliim.com/product/blue-nile-cushion/')
                splash:wait(1.5)
                return splash:url()
            end
            """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute',
                            args={'lua_source': self.script})

    def parse(self, response):
        inspect_response(response, self)
        #yield {'test_body': response.body_as_unicode()}



if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(HefnaSpiderSpider)
    process.start() # the script will block here until the crawling is finished


