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

    script = """
    function main(splash)
      splash:go('https://kiliim.com/shop/')
      local currency = splash:evaljs('document.querySelectorAll("span.woocommerce-Price-currencySymbol")[0].innerHTML')
      local ok = 1
      if currency ~= "EGP" then
          ok = 0
      end
      splash:go('https://kiliim.com/product/blue-nile-cushion/')
      local button = splash:select('button.single_add_to_cart_button')
      button:mouse_click()
      splash:wait(15)
      splash:go('https://kiliim.com/checkout/')
      splash:wait(15)
      -- local select_input = splash:select('span[id=select2-chosen-1]')
      -- select_input:mouse_click()
      -- splash:wait(15)
      local country = splash:select('input[id=s2id_autogen1_search]')
      country:send_text("France")
      country:send_keys("<Return>")
      splash:wait(5)
      splash:go('https://kiliim.com/product/blue-nile-cushion/')
      return {html=splash:html()}
    end
    """

    script_alt = """
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
        local currency = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
        -- strip spaces
        currency = currency:gsub("%s+", "")
        -- check if currency is correct
        if currency ~= "$" then
          splash:unlock_navigation()
          splash:set_viewport_full()
          splash:go('https://kiliim.com/product/blue-nile-cushion/')
          -- local cart_btn = splash:select('button[type=submit]')
          -- local bounds = cart_btn:bounds()
          -- assert(cart_btn:mouse_click{x=bounds.width/2, y=bounds.height/2})
          splash:wait(3)
          local button = splash:select('button.single_add_to_cart_button')
          button:mouse_click()
          splash:wait(5)
          -- local view_btn splash:select('a.wc-forward')
          -- local view_bounds = view_btn:bounds()
          -- assert(view_btn:mouse_click{x=view_bounds.width/2, y=view_bounds.height/2})
          -- splash:wait(50)
          splash:go('https://kiliim.com/checkout/')
          splash:wait(5)
          local select_input = splash:select('span#select2-chosen-1')
          select_input:mouse_click()
          splash:wait(5)
          local country = splash:select('input[id=s2id_autogen1_search]')
          country:send_text("France")
          country:send_keys("<Tab>")
          splash:wait(20)
          local option_select = splash:evaljs('document.getElementById("billing_country").value')
          splash:evaljs('document.getElementById("billing_country").value="FR"')
          splash:wait(5)
          -- #billing_email
          local email = splash:select('input[id=billing_email]')
          email:send_text("test@test.com")
          email:send_keys("<Tab>")
          splash:wait(5)
          -- h3#ship-to-different-address-checkbox
          local update_billing = splash:select('h3#ship-to-different-address')
          update_billing:mouse_click()
          splash:wait(5)
          -- get td.product-total
          local test_data = splash:evaljs('document.querySelector("td.product-total")')
          -- get .select2-match which should be the country
          -- local country_name = splash:evaljs('document.querySelector("#select2-chosen-1").innerHTML'):gsub("%s+", "")
          -- now click on it via .select2-result-label
          -- local select_country = splash:select('.select2-result')
          -- select_country:mouse_click()
          -- splash:wait(10)
          -- splash:go('https://kiliim.com/product/burgundy-scattered-stitch-cushion/')
          -- currency = bounds
          -- splash:wait(5)
          -- splash:go('https://kiliim.com/product/burgundy-scattered-stitch-cushion/')
          -- splash:wait(20)
          local currency_test = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML'):gsub("%s+", "")
        end
        splash:wait(0.5)
        local entries = splash:history()
        local last_response = entries[#entries].response
        return {
            currency = currency_test,
            test = test_data,
            test2 = option_select,
            url = splash:url(),
            headers = last_response.headers,
            http_status = last_response.status,
            cookies = splash:get_cookies(),
            html = splash:html()
        }
    end
    """

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
        -- no timeout
        splash.resource_timeout = 0
        local currency = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
        -- strip spaces
        currency = currency:gsub("%s+", "")
        -- check if currency is correct
        if currency ~= "EUR" then
          splash:unlock_navigation()
          splash:set_viewport_full()
          splash:go('https://kiliim.com/product/blue-nile-cushion/')
          splash:wait(10)
          local button = splash:select('button.single_add_to_cart_button')
          button:mouse_click()
          splash:wait(10)
          -- splash:go('https://kiliim.com/checkout/')
          -- splash:wait(10)
          -- local select_input = splash:select('span[id=select2-chosen-1]')
          -- select_input:mouse_click()
          -- splash:wait(10)
          -- local country = splash:select('input[id=s2id_autogen1_search]')
          -- local currency_check = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
          -- ok, err = country:send_text("France")
          -- ok, err = country:send_keys("<Tab>")
          -- splash:wait(24)

          -- while currency_check =="EGP" do
          --   splash:wait(5)
          --   currency_check = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML'):gsub("%s+", "")
          -- end
          -- splash:go('https://kiliim.com/product/burgundy-scattered-stitch-cushion/')
          -- splash:wait(10)
          -- local currency_test = splash:evaljs('document.querySelector("span.woocommerce-Price-currencySymbol").innerHTML')
        end
        splash:wait(0.5)
        local entries = splash:history()
        local last_response = entries[#entries].response
        return {
            png = splash:png(),
            -- har = splash:har(),
            currency = currency,
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
                        'wait': 100,
                        # set rendering arguments here
                        'html': 1,
                        # 'images': 0,
                        'png': 1,

                        # 'url' is prefilled from request url
                        # 'http_method' is set to 'POST' for POST requests
                        # 'body' is set to request body for POST requests
                    },
                    # optional parameters
                    'splash_headers': {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
                                       'Host': 'kiliim.com',
                                       },
                    # 'cache_args': ['lua_source'],
                    'endpoint': 'execute',  # optional; default is render.json
                    # 'splash_url': '<url>',      # optional; overrides SPLASH_URL
                    'slot_policy': SlotPolicy.PER_DOMAIN,
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
        #inspect_response(response, self)
        yield {'test_body': response.body_as_unicode()}
