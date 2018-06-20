# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.shell import inspect_response
from scrapy.crawler import CrawlerProcess
# from scrapy_splash import SplashRequest
from scrapy_splash import SlotPolicy

###
#  sudo docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash --max-timeout 3600 --disable-lua-sandbox
###


class AlphaSpider(scrapy.Spider):
    name = 'alpha'

    allowed_domains = ['kiliim.com']
    start_urls = ['https://kiliim.com/shop']

    script_alt2 = """
    function main(splash)
        splash:init_cookies(splash.args.cookies)
        local ok,reason = splash:go{
          splash.args.url,
          headers=splash.args.headers,
          http_method=splash.args.http_method,
          body=splash.args.body,
        }
        splash:wait(0.5)
        splash.private_mode_enabled = false
        -- disable timeout for resources
        splash.resource_timeout = 0
        local currency = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
        -- strip off the spaces
        currency = currency:gsub("%s+", "")

        -- update cookies on each response
        splash:on_response_headers(function(response)
                local response_cookies = response.headers["Set-cookie"]
                cookies = cookies .. ";" .. response_cookies
                response.abort()
            end)

        -- check if currency is correct
        if currency ~= "EUR" then
          splash:unlock_navigation()
          splash:set_viewport_full()
          -- grab a known product
          splash:go('https://kiliim.com/product/blue-nile-cushion/')
          splash:wait(10)
          -- add it to cart
          local button = splash:select('button.single_add_to_cart_button')
          button:mouse_click()
          splash:wait(10)
          -- go to checkout
          splash:go('https://kiliim.com/checkout/')
          splash:wait(10)
          -- click on country dropdown
          local select_input = splash:select('span[id=select2-chosen-1]')
          select_input:mouse_click()
          splash:wait(10)
          local country = splash:select('input[id=s2id_autogen1_search]')
          local currency_check = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
          -- type the country name and hit Tab
          ok, err = country:send_text("France")
          ok, err = country:send_keys("<Tab>")
          -- splash:wait(50)
          -- wait till currency changes
          while currency_check == "EGP" do
            splash:wait(5)
            currency_check = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML'):gsub("%s+", "")
          end
          -- splash:go('https://kiliim.com/product/burgundy-scattered-stitch-cushion/')
          -- splash:wait(10)
          -- local shop = splash:select('ul#menu-main-menu-2>li.menu-item-24>a')
          -- shop:mouse_click()
          -- splash:wait(10)
          -- local currency_test = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
        end

        splash:wait(1)
        -- now retrieve the original URL
        ok,reason = splash:go(splash.args.url)
        splash:wait(3)

        splash:wait(0.5)
        local entries = splash:history()
        local last_response = entries[#entries].response
        return {
            png = splash:png(),
            -- har = splash:har(),
            currency = currency_test,
            url = splash:url(),
            -- headers = last_response.headers,
            -- http_status = last_response.status,
            -- cookies = splash:get_cookies(),
            -- html = splash:html()
        }
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse_result, meta={
                'splash': {
                    'args': {
                        'lua_source': self.script_alt2,
                        'timeout': 3600,
                        'render_all': 1,
                        # 'wait': 100,
                        # set rendering arguments here
                        'html': 1,
                        # 'images': 0,
                        'png': 1,

                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # optional parameters
                    # 'splash_headers': {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
                    #                   'Host': 'kiliim.com',
                    #                   },
                    # 'cache_args': ['lua_source'],
                    'endpoint': 'execute',  # optional; default is render.json
                    # 'splash_url': '<url>',      # optional; overrides SPLASH_URL
                    'slot_policy': SlotPolicy.SINGLE_SLOT,
                    # 'splash_headers': {},       # optional; a dict with headers sent to Splash
                    # 'dont_process_response': True,  # optional, default is False
                    'dont_send_headers': False,  # optional, default is False
                    'magic_response': False,    # optional, default is True
                    'session_id': 'alpha_session',
                }
            })

            # yield SplashRequest(url, self.parse, endpoint='execute',
            #                     args={'lua_source': self.script_alt,
            #                           'timeout': 3600},
            #                     'session_id': 'alpha',
            #                     'new_session_id': 'test',
            #                     # cache_args='lua_source'
            #                     )

    def parse_result(self, response):
        # inspect_response(response, self)
        yield {'response': response.body_as_unicode()}
