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
            self.parts, response.request.url, "digikey.sg"
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
                cleaned_all["props"]["pageProps"]["envelope"]["data"]["priceQuantity"][
                    "pricing"
                ][0]["pricingTiers"]
            )

            description = string_cleaning(
                response.xpath(
                    "//tr[@data-testid='detailed-description']/td[2]/div/text()"
                ).get()
            )
            selling_length = None
            if part_requirement["UOM"] == "M":
                selling_length = get_selling_length(description, "digikey.sg")
            mfg_pn = ""
            if part_requirement["found_in_item_master"] == True:
                mfg_pn = string_cleaning(
                    response.xpath("//td[@data-testid='mfr-number']/div/text()").get()
                )
            else:
                mfg_pn = part_requirement["mfg_pn"]

            # sold_in_bag = cleaned_all["props"]["pageProps"]["envelope"]["data"][
            #     "priceQuantity"
            # ]["pricing"][0]["packaging"]
            # if sold_in_bag != None and "per Pkg" in sold_in_bag:
            #     sold_in_bag = int(string_cleaning(sold_in_bag.replace("per Pkg", "")))
            # else:
            #     sold_in_bag = None

            lead_time = response.xpath("//div[@id='stdLeadTime']/text()").get()
            if lead_time != None:
                lead_time = (
                    int(string_cleaning(lead_time.lower().replace("weeks", ""))) * 7
                )
            yield {
                "mfg_pn": mfg_pn,
                "description": description,
                "selling_length": selling_length,
                "url": response.request.url,
                "pricing_table": pricing,
                "delivery_days": {"min": 2, "max": 4},
                "quantity_available": quantity_available,
                "sold_in_bag": None,
                "lead_time": lead_time,
            }

    def get_pricing_table(self, raw_table):
        pricing = []
        for idx, price in enumerate(raw_table):
            max_qty = 1000000
            if idx < len(raw_table) - 1:
                max_qty = int(
                    string_cleaning(raw_table[idx + 1]["breakQty"].replace(",", ""))
                )
            pricing.append(
                {
                    "min_quantity": int(
                        string_cleaning(price["breakQty"].replace(",", ""))
                    ),
                    "max_quantity": max_qty - 1,
                    "unit_price": float(
                        string_cleaning(
                            price["unitPrice"].replace("$", "").replace(",", "")
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
