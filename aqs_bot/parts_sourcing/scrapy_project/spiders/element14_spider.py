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


class Element14Spider(scrapy.Spider):

    name = "element14"

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
        if "sg.element14.com" in part["supplier_links"]:
            start_urls.append(part["supplier_links"]["sg.element14.com"][0])

    custom_settings = {
        "FEED_URI": "../../output/element14_scrapped_data.json",
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
        "element14_scrapped_data.json",
    )
    if os.path.exists(filePath):
        os.remove(filePath)

    def parse(self, response):

        part_requirement = get_part_requirements(
            self.parts_from_file,
            response.xpath('//dd[@class="ManufacturerPartNumber"]/span/text()').get(),
        )

        quantity_available = int(
            string_cleaning(
                response.xpath('//span[@class="availTxtMsg"]/text()')
                .get()
                .replace(",", "")
                .replace("In stock", "")
            )
        )

        if validate_part_brand(
            response.xpath('//span[@class="schemaOrg"]/text()').get(),
            part_requirement["DESCRIPTION"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["QTY"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath('//tr[starts-with(@class, "data-product-pricerow")]')
            )

            yield {
                "mfg_pn": string_cleaning(
                    response.xpath(
                        '//dd[@class="ManufacturerPartNumber"]/span/text()'
                    ).get()
                ),
                "description": string_cleaning(
                    response.xpath("//span[@class='pdpGreyText']/text()").get()
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
                    "quantity": string_cleaning(price.xpath("td/text()").get()),
                    "unit_price": string_cleaning(price.xpath("td/span/text()").get()),
                    "extended price": None,
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def element14_crawl():
    yield runner.crawl(Element14Spider)
    reactor.stop()


element14_crawl()
reactor.run()
