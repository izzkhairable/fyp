import scrapy
import json
import os
from urllib.parse import unquote, urlparse
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer


class GoogleSpider(scrapy.Spider):
    name = "google"

    suppliers_raw = open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../input",
            "suppliers.json",
        )
    )
    file_title = "C1000014DrevB.json"
    parts_raw = open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../../input", file_title
        )
    )
    suppliers = json.load(suppliers_raw)
    parts = json.load(parts_raw)

    start_urls = []
    for part in parts:
        mfg_pn_encoded = "+".join(part["MFG PN."].split(" "))
        start_urls.append(f"https://www.google.com/search?q={mfg_pn_encoded}")

    filePath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../output",
        "google_result.json",
    )
    if os.path.exists(filePath):
        os.remove(filePath)

    custom_settings = {
        "FEED_URI": "../../output/google_result.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }

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
            "file_title": self.file_title,
            "mfg_pn": response.request.url.replace(
                "https://www.google.com/search?q=", ""
            ).replace("+", ""),
            "supplier_links": links_dict,
        }


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def google_crawl():
    yield runner.crawl(GoogleSpider)
    reactor.stop()


google_crawl()
reactor.run()
