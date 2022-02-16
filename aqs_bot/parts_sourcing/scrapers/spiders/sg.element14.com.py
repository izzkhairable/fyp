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


class Element14Spider(scrapy.Spider):

    name = "element14"

    custom_settings = {
        "FEED_URI": "./output/%(file_title)s_element14_scrapped_data.json",
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

        self.start_urls = []
        for part in self.parts:
            if "sg.element14.com" in part["supplier_links"]:
                self.start_urls.append(part["supplier_links"]["sg.element14.com"][0])

        self.user_agent = "PostmanRuntime/7.28.3"

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_element14_scrapped_data.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(Element14Spider, self).__init__(*args, **kwargs)

    def parse(self, response):

        part_requirement = get_part_requirements(
            self.parts, response.request.url, "sg.element14.com"
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
            part_requirement["description"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["quantity"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath('//tr[starts-with(@class, "data-product-pricerow")]')
            )
            description = string_cleaning(
                response.xpath("//span[@class='pdpGreyText']/text()").get()
            )
            selling_length = None
            if part_requirement["UOM"] == "M":
                selling_length = get_selling_length(description, "sg.element14.com")

            mfg_pn = ""
            if part_requirement["found_in_item_master"] == True:
                mfg_pn = string_cleaning(
                    response.xpath(
                        '//dd[@class="ManufacturerPartNumber"]/span/text()'
                    ).get()
                )
            else:
                mfg_pn = part_requirement["mfg_pn"]

            sold_in_bag = response.xpath(
                '//dl[@id="unitMesureSection"]/dd/strong/text()'
            ).get()
            if sold_in_bag != None and "Pack of" in sold_in_bag:
                sold_in_bag = int(string_cleaning(sold_in_bag.replace("Pack of", "")))
            else:
                sold_in_bag = None

            yield {
                "mfg_pn": mfg_pn,
                "description": description,
                "selling_length": selling_length,
                "url": response.request.url,
                "pricing_table": pricing,
                "delivery_days": {"min": 2, "max": 4},
                "quantity_available": quantity_available,
                "sold_in_bag": sold_in_bag,
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
                        .replace("+", "")
                    )
                )
            pricing.append(
                {
                    "min_quantity": int(
                        string_cleaning(price.xpath("td/text()").get().replace("+", ""))
                    ),
                    "max_quantity": max_qty - 1,
                    "unit_price": float(
                        string_cleaning(
                            price.xpath("td/span/text()").get().replace("S$", "")
                        )
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def element14_crawl(file_title):
    yield runner.crawl(Element14Spider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    element14_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
