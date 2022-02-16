import scrapy
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
import json
import os
from helper_functions import string_cleaning
import sys


class SchneiderSpider(scrapy.Spider):

    name = "schneider"

    custom_settings = {
        "FEED_URI": "./output/%(file_title)s_schneider_scrapped_data.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOAD_DELAY": 2,
    }

    def __init__(self, *args, **kwargs):
        self.file_title = kwargs.get("file_title")
        self.parts_raw = open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../output",
                f"{self.file_title}_google_result.json",
            )
        )
        self.parts = json.load(self.parts_raw)
        # self.parts_from_file_raw = open(
        #     os.path.join(
        #         os.path.dirname(os.path.abspath(__file__)),
        #         "../../input",
        #         self.file_title + ".json",
        #     )
        # )
        # self.parts_from_file = json.load(self.parts_from_file_raw)
        self.user_agent = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"
        self.start_urls = []
        for part in self.parts:
            if "se.com" in part["supplier_links"]:
                self.start_urls.append(part["supplier_links"]["se.com"][0])

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_schneider_scrapped_data.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(SchneiderSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        mfg_pn = string_cleaning(
            response.xpath(
                "//h2[@class='main-product-info__bottom-item main-product-info__bottom-item--product-id sc-pes-main-product-info']/text()"
            ).get()
        )
        description = string_cleaning(
            response.xpath(
                "//h1[contains(@class, 'main-product-info__description')]/text()"
            ).get()
        )

        yield {
            "mfg_pn": mfg_pn,
            "description": description,
            "url": response.request.url,
            "pricing_table": None,
            "selling_length": None,
            "delivery_days": None,
            "quantity_available": None,
        }


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def schneider_crawl(file_title):
    yield runner.crawl(SchneiderSpider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    schneider_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
