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
from get_rsonline_lead_time import get_rsonline_lead_time
from datetime import datetime


class RsonlineSpider(scrapy.Spider):

    name = "rsonline"

    custom_settings = {
        "FEED_URI": "./output/%(file_title)s_rsonline_scrapped_data.json",
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
            if "sg.rs-online.com" in part["supplier_links"]:
                self.start_urls.append(part["supplier_links"]["sg.rs-online.com"][0])

        self.filePath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{self.file_title}_rsonline_scrapped_data.json",
        )
        if os.path.exists(self.filePath):
            os.remove(self.filePath)
        super(RsonlineSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        part_requirement = get_part_requirements(
            self.parts, response.request.url, "sg.rs-online.com"
        )

        manufacturer = ""
        mfg_pn = ""
        if part_requirement["found_in_item_master"] == False:
            mfg_pn = part_requirement["mfg_pn"]
        elif (
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

        raw_qty = string_cleaning(
            response.xpath("//div[@data-testid='stock-status-0']/text()").get()
        )
        quantity_available = 0
        if raw_qty.isnumeric():
            quantity_available = int(raw_qty)

        if validate_part_brand(
            manufacturer,
            part_requirement["description"].lower(),
        ) and validate_quantity_available(
            quantity_available,
            part_requirement["quantity"],
            part_requirement["UOM"],
        ):
            pricing = self.get_pricing_table(
                response.xpath(
                    "//div[@data-testid='desktop']//table[@data-testid='price-breaks']/tbody/tr"
                )
            )
            description = string_cleaning(
                response.xpath("//h1[@data-testid='long-description']/text()").get()
            )
            selling_length = None
            if part_requirement["UOM"] == "M":
                selling_length = get_selling_length(description, "sg.rs-online.com")

            sold_in_bag = response.xpath(
                '//p[@data-testid="price-heading"]/text()'
            ).get()
            if sold_in_bag != None and "Price 1 Bag of" in sold_in_bag:
                sold_in_bag = int(
                    string_cleaning(sold_in_bag.replace("Price 1 Bag of", ""))
                )
            else:
                sold_in_bag = None

            lead_time = get_rsonline_lead_time(response.request.url)
            print("Yo this is lead_time", lead_time)
            if lead_time != None:
                lead_time = lead_time.split(" back order for despatch ")[1][0:10]
                diff_delta = datetime.strptime(lead_time, "%d/%m/%Y") - datetime.now()
                lead_time = diff_delta.days
            yield {
                "mfg_pn": mfg_pn,
                "description": description,
                "url": response.request.url,
                "pricing_table": pricing,
                "selling_length": selling_length,
                "delivery_days": {"min": 2, "max": 4},
                "quantity_available": quantity_available,
                "sold_in_bag": sold_in_bag,
                "lead_time": lead_time,
            }

    def get_pricing_table(self, raw_table):
        pricing = []
        for idx, price in enumerate(raw_table):
            max_qty = 1000000
            if idx < len(raw_table) - 1:
                max_qty = int(
                    string_cleaning(
                        price.xpath(
                            "td[1]/text()",
                        )
                        .get()
                        .split(" - ")[1]
                        .replace("+", "")
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
                            .split(" - ")[0]
                            .replace("+", "")
                        )
                    ),
                    "max_quantity": max_qty,
                    "unit_price": float(
                        string_cleaning(
                            price.xpath(
                                "td[2]/text()",
                            )
                            .get()
                            .replace("SGD", "")
                        )
                    ),
                }
            )
        return pricing


configure_logging()
runner = CrawlerRunner()


@defer.inlineCallbacks
def rsonline_crawl(file_title):
    yield runner.crawl(RsonlineSpider, file_title=file_title)
    reactor.stop()


def main_func(file_title):
    rsonline_crawl(file_title)
    reactor.run()


if __name__ == "__main__":
    main_func(sys.argv[1])
