from curses import raw
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


class MouserSpider(scrapy.Spider):

    name = "mouser"

    custom_settings = {
        "FEED_URI": "../../output/%(file_title)s_mouser_scrapped_data.json",
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
            if "mouser.sg" in part["supplier_links"]:
                self.start_urls.append(part["supplier_links"]["mouser.sg"][0])

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_mouser_scrapped_data.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(MouserSpider, self).__init__(*args, **kwargs)

    def parse(self, response):

        part_requirement = get_part_requirements(
            self.parts_from_file,
            response.xpath("//span[@id='spnManufacturerPartNumber']/text()").get(),
        )

        quantity_available = 0
        if (
            response.xpath('//h2[@class="panel-title pdp-pricing-header"]/text()')
            .get()
            .find("Availability")
            == -1
        ):
            quantity_available = int(
                string_cleaning(
                    response.xpath(
                        '//h2[@class="panel-title pdp-pricing-header"]/text()'
                    )
                    .get()
                    .replace("In Stock:", "")
                    .replace(",", "")
                )
            )
        else:
            quantity_available = int(
                string_cleaning(
                    response.xpath('//div[@class="col-xs-3 onOrderQuantity"]/text()')
                    .get()
                    .replace(",", "")
                )
            )

        if validate_part_brand(
            response.xpath("//a[@id='lnkManufacturerName']/text()").get(),
            part_requirement["description"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["quantity"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath('//table[@class="pricing-table"]/tbody/tr')
            )
            description = string_cleaning(
                response.xpath('//span[@id="spnDescription"]/text()').get()
            )
            selling_length = None
            if part_requirement["UOM"] == "M":
                selling_length = get_selling_length(description, "mouser.sg")

            yield {
                "mfg_pn": string_cleaning(
                    response.xpath(
                        '//span[@id="spnManufacturerPartNumber"]/text()'
                    ).get()
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
        if raw_table[-1].xpath("th/a/text()").get() == None:
            raw_table = raw_table[0:-1]
        for idx, price in enumerate(raw_table):
            if (
                price.xpath(
                    "th/a/text()",
                )
                == []
                or price.xpath(
                    "th/a/text()",
                )
                == None
            ):
                continue
            max_qty = 1000000
            if idx < len(raw_table) - 1:
                max_qty = int(
                    string_cleaning(
                        raw_table[idx + 1]
                        .xpath(
                            "th/a/text()",
                        )
                        .get()
                    )
                )
            pricing.append(
                {
                    "min_quantity": int(
                        string_cleaning(
                            price.xpath(
                                "th/a/text()",
                            ).get()
                        )
                    ),
                    "max_quantity": max_qty - 1,
                    "unit_price": float(
                        string_cleaning(
                            price.xpath(
                                "td/text()",
                            )
                            .getall()[0]
                            .replace("$", "")
                        )
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def mouser_crawl(file_title):
    yield runner.crawl(MouserSpider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    mouser_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
