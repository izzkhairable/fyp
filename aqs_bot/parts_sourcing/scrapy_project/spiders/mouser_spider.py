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


class MouserSpider(scrapy.Spider):

    name = "mouser"

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
        if "mouser.sg" in part["supplier_links"]:
            start_urls.append(part["supplier_links"]["mouser.sg"][0])

    custom_settings = {
        "FEED_URI": "../../output/mouser_scrapped_data.json",
        "FEED_FORMAT": "json",
        "FEED_EXPORTERS": {
            "json": "scrapy.exporters.JsonItemExporter",
        },
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    filePath = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../../output",
        "mouser_scrapped_data.json",
    )
    if os.path.exists(filePath):
        os.remove(filePath)

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
            part_requirement["DESCRIPTION"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["QTY"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath('//table[@class="pricing-table"]/tbody/tr')
            )

            yield {
                "mfg_pn": string_cleaning(
                    response.xpath(
                        '//span[@id="spnManufacturerPartNumber"]/text()'
                    ).get()
                ),
                "description": string_cleaning(
                    response.xpath('//span[@id="spnDescription"]/text()').get()
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
            pricing.append(
                {
                    "quantity": string_cleaning(
                        price.xpath(
                            "th/a/text()",
                        ).get()
                    ),
                    "unit_price": string_cleaning(
                        price.xpath(
                            "td/text()",
                        ).getall()[0]
                    ),
                    "extended price": string_cleaning(
                        price.xpath(
                            "td/text()",
                        ).getall()[1]
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def mouser_crawl():
    yield runner.crawl(MouserSpider)
    reactor.stop()


mouser_crawl()
reactor.run()
