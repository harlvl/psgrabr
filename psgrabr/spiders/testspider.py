import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from datetime import datetime,timedelta

from psgrabr.items import ScrapyProjectItem

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestSpider(CrawlSpider):
    name = "testspider"
    item_count = 0
    allowed_domains = ['grabr.io']
    # start_urls = ['https://grabr.io/es/login']
    start_urls = ['https://twitter.com/']

    def parse(self, response):
        # geckodriver = 'C:\\Users\\hlvl\\\Documents\\\geckodriver\\geckodriver.exe'
        basepath ='https://grabr.io/es'

        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')

        # self.driver = webdriver.Firefox(executable_path=geckodriver, firefox_options=options)
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.get(response.url)
        self.driver.save_screenshot('C:\\Users\\hlvl\\Downloads\\nohead.png')
        self.driver.quit()