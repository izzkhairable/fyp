import os
import sys

file_title = "26VSMTC-0012-ST=14.json".replace(".json", "")
# file_title = "test_bs.json".replace(".json", "")
os.system(f"python ./scrapers/spiders/google_search_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/mouser_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/digikey_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/element14_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/rsonline_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/misumi_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/harting_spider.py {file_title}")
os.system(f"python ./scrapers/spiders/schneider_spider.py {file_title}")
os.system(f"python ./combiners/combine_results.py {file_title}")
os.system(f"python ./calculators/find_unit_price_quantity.py {file_title}")
os.system(f"python ./calculators/find_best_supplier.py {file_title}")
os.system(f"python ./combiners/combine_final_results.py {file_title}")


# os.system("python test_spider.py")
