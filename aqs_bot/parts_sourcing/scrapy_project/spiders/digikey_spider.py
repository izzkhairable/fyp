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
    get_selling_length,
)
import sys


class DigikeySpider(scrapy.Spider):

    name = "digikey"

    custom_settings = {
        "FEED_URI": "./output/%(file_title)s_digikey_scrapped_data.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
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
        self.parts_from_file_raw = open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../input",
                self.file_title + ".json",
            )
        )
        self.parts_from_file = json.load(self.parts_from_file_raw)

        self.start_urls = []
        for part in self.parts:
            if "digikey.sg" in part["supplier_links"]:
                self.start_urls.append(part["supplier_links"]["digikey.sg"][0])

        self.user_agent = "PostmanRuntime/7.28.3"

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_digikey_scrapped_data.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(DigikeySpider, self).__init__(*args, **kwargs)

    def parse(self, response):

        part_requirement = get_part_requirements(
            self.parts_from_file,
            response.xpath("//td[@data-testid='mfr-number']/div/text()").get(),
        )

        raw = response.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        cleaned_all = json.loads(raw)

        quantity_available = None
        if (
            "qtyAvailable"
            in cleaned_all["props"]["pageProps"]["envelope"]["data"]["priceQuantity"]
        ):
            quantity_available = int(
                string_cleaning(
                    cleaned_all["props"]["pageProps"]["envelope"]["data"][
                        "priceQuantity"
                    ]["qtyAvailable"].replace(",", "")
                )
            )
        if quantity_available == None:
            quantity_available = int(
                string_cleaning(
                    cleaned_all["props"]["pageProps"]["envelope"]["data"]["messages"][
                        0
                    ]["message"]
                    .replace("Factory Stock:", "")
                    .replace(",", "")
                )
            )
        if validate_part_brand(
            response.xpath(
                "//tr[@data-testid='overview-manufacturer']/td[2]/div/text()"
            ).get(),
            part_requirement["description"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["quantity"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath(
                    '//table[starts-with(@data-testid,"pricing-table")]/tbody/tr'
                )
            )
            description = string_cleaning(
                response.xpath(
                    "//tr[@data-testid='detailed-description']/td[2]/div/text()"
                ).get()
            )
            selling_length = None
            if part_requirement["UOM"] == "M":
                selling_length = get_selling_length(description, "digikey.sg")
            yield {
                "mfg_pn": string_cleaning(
                    response.xpath("//td[@data-testid='mfr-number']/div/text()").get()
                ),
                "description": description,
                "selling_length": selling_length,
                "url": response.request.url,
                "pricing_table": pricing,
                "delivery_days": {"min": 2, "max": 4},
                "quantity_available": quantity_available,
            }

    def get_pricing_table(self, raw_table):
        pricing = []
        for idx, price in enumerate(raw_table):
            max_qty = 1000000
            if idx < len(raw_table) - 1:
                max_qty = int(
                    string_cleaning(
                        raw_table[idx + 1]
                        .xpath(
                            "td[1]/text()",
                        )
                        .get()
                        .replace(",", "")
                    )
                )
            pricing.append(
                {
                    "min_quantity": int(
                        string_cleaning(
                            price.xpath(
                                "td[1]/text()",
                            )
                            .get()
                            .replace(",", "")
                        )
                    ),
                    "max_quantity": max_qty - 1,
                    "unit_price": float(
                        string_cleaning(
                            price.xpath(
                                "td[2]/text()",
                            )
                            .get()
                            .replace("$", "")
                            .replace(",", "")
                        )
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def digikey_crawl(file_title):
    yield runner.crawl(DigikeySpider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    digikey_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
