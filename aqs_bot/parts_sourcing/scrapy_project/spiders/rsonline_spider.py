import scrapy
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
import json
import os
from helper_functions import (
    string_cleaning,
    get_part_requirements,
    validate_part_brand,
    validate_quantity_available,
)


class RsonlineSpider(scrapy.Spider):

    name = "rsonline"

    parts_raw = open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            "google_result.json",
        )
    )
    parts = json.load(parts_raw)
    parts_from_file_raw = open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../input",
            parts[0]["file_title"],
        )
    )
    parts_from_file = json.load(parts_from_file_raw)

    start_urls = []
    for part in parts:
        if "sg.rs-online.com" in part["supplier_links"]:
            start_urls.append(part["supplier_links"]["sg.rs-online.com"][0])

    custom_settings = {
        "FEED_URI": "../../output/rsonline_scrapped_data.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    filePath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../output",
        "rsonline_scrapped_data.json",
    )
    if os.path.exists(filePath):
        os.remove(filePath)

    def parse(self, response):
        mfg_pn = ""
        manufacturer = ""
        if (
            response.xpath(
                "//dl[@data-testid='key-details-desktop']/dd[2]/text()"
            ).get()
            == None
        ):
            mfg_pn = response.xpath(
                "//dl[@data-testid='key-details-desktop']/dd[1]/text()"
            ).get()

            manufacturer = response.xpath(
                "//dl[@data-testid='key-details-desktop']/dd[2]/a/text()"
            ).get()
        else:
            mfg_pn = response.xpath(
                "//dl[@data-testid='key-details-desktop']/dd[2]/text()"
            ).get()
            manufacturer = response.xpath(
                "//dl[@data-testid='key-details-desktop']/dd[3]/a/text()"
            ).get()
        part_requirement = get_part_requirements(
            self.parts_from_file,
            mfg_pn,
        )

        raw_qty = string_cleaning(
            response.xpath("//div[@data-testid='stock-status-0']/text()").get()
        )
        quantity_available = 0
        if raw_qty.isnumeric():
            quantity_available = int(raw_qty)

        if validate_part_brand(
            manufacturer,
            part_requirement["DESCRIPTION"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["QTY"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath(
                    "//div[@data-testid='desktop']//table[@data-testid='price-breaks']/tbody/tr"
                )
            )

            yield {
                "mfg_pn": mfg_pn,
                "description": string_cleaning(
                    response.xpath("//h1[@data-testid='long-description']/text()").get()
                ),
                "url": response.request.url,
                "pricing_table": pricing,
                "delivery_days": {"min": 2, "max": 4},
                "quantity_available": quantity_available,
                "customer_part_requirement": part_requirement,
            }

    def get_pricing_table(self, raw_table):
        pricing = []
        for price in raw_table:
            pricing.append(
                {
                    "quantity": string_cleaning(
                        price.xpath(
                            "td[1]/text()",
                        ).get()
                    ),
                    "unit_price": string_cleaning(
                        price.xpath(
                            "td[2]/text()",
                        ).get()
                    ),
                    "extended price": string_cleaning(
                        price.xpath(
                            "td[3]/text()",
                        ).get()
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def rsonline_crawl():
    yield runner.crawl(RsonlineSpider)
    reactor.stop()


rsonline_crawl()
reactor.run()
