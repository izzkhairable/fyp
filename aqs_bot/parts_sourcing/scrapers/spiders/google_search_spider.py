import scrapy
import json
import os
from urllib.parse import unquote, urlparse
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
import sys


class GoogleSpider(scrapy.Spider):
    name = "google"

    custom_settings = {
        "FEED_URI": "./output/%(file_title)s_google_result.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOAD_DELAY": 5,
    }

    def __init__(self, *args, **kwargs):
        self.file_title = kwargs.get("file_title")
        self.suppliers_raw = open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../input",
                "suppliers.json",
            )
        )
        self.parts_raw = open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../input",
                self.file_title + ".json",
            )
        )
        self.suppliers = json.load(self.suppliers_raw)
        self.parts = json.load(self.parts_raw)

        self.start_urls = []
        for part in self.parts["quotation_component"]:
            mfg_pn = part["mfg_pn"]
            if mfg_pn == None:
                mfg_pn = part["description"]
            mfg_pn_encoded = "+".join(mfg_pn.split(" "))
            self.start_urls.append(f"https://www.google.com/search?q={mfg_pn_encoded}")

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_google_result.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(GoogleSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        links_dict = {}
        for link in response.xpath("//div/div/a/@href"):
            if "/url?q=" in link.get() and "google.com" not in link.get():
                pos_of_extra = unquote(link.get()).replace("/url?q=", "").find("&sa")
                url = unquote(link.get()).replace("/url?q=", "")[0:pos_of_extra]
                domain = urlparse(url).netloc.replace("www.", "")
                if domain in self.suppliers:
                    if domain in links_dict:
                        links_dict[domain].append(url)
                    else:
                        links_dict[domain] = [url]

        yield {
            "description_or_mfg_pn": response.request.url.replace(
                "https://www.google.com/search?q=", ""
            ).replace("+", " "),
            "supplier_links": links_dict,
            "item": response.xpath("/").get(),
        }


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def google_crawl(file_title):
    yield runner.crawl(GoogleSpider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    google_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
