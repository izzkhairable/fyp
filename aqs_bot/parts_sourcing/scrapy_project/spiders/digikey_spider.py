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


class DigikeySpider(scrapy.Spider):

    name = "digikey"

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
        if "digikey.sg" in part["supplier_links"]:
            start_urls.append(part["supplier_links"]["digikey.sg"][0])

    custom_settings = {
        "FEED_URI": "../../output/digikey_scrapped_data.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }
    user_agent = "PostmanRuntime/7.28.3"

    filePath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../output",
        "digikey_scrapped_data.json",
    )
    if os.path.exists(filePath):
        os.remove(filePath)

    def parse(self, response):

        part_requirement = get_part_requirements(
            self.parts_from_file,
            response.xpath("//td[@data-testid='mfr-number']/div/text()").get(),
        )

        raw = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        cleaned_all = json.loads(raw)
        quantity_available = int(
            string_cleaning(
                cleaned_all["props"]["pageProps"]["envelope"]["data"]["priceQuantity"][
                    "qtyAvailable"
                ].replace(",", "")
            )
        )

        if validate_part_brand(
            response.xpath(
                "//tr[@data-testid='overview-manufacturer']/td[2]/div/text()"
            ).get(),
            part_requirement["DESCRIPTION"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["QTY"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath(
                    '//table[starts-with(@data-testid,"pricing-table")]/tbody/tr'
                )
            )

            yield {
                "mfg_pn": string_cleaning(
                    response.xpath("//td[@data-testid='mfr-number']/div/text()").get()
                ),
                "description": string_cleaning(
                    response.xpath(
                        "//tr[@data-testid='detailed-description']/td[2]/div/text()"
                    ).get()
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
def digikey_crawl():
    yield runner.crawl(DigikeySpider)
    reactor.stop()


digikey_crawl()
reactor.run()
