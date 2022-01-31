import os
import sys

file_title = "26VSMTC-0012-ST=14.json".replace(".json", "")
# file_title = "test_bs.json".replace(".json", "")
os.system(f"python google_search_spider.py '{file_title}'")
os.system(f"python mouser_spider.py '{file_title}'")
os.system(f"python digikey_spider.py '{file_title}'")
os.system(f"python element14_spider.py '{file_title}'")
os.system(f"python rsonline_spider.py '{file_title}'")
os.system(f"python misumi_spider.py '{file_title}'")
os.system(f"python harting_spider.py '{file_title}'")
os.system(f"python schneider_spider.py '{file_title}'")
os.system(f"python combine_results.py '{file_title}'")
os.system(f"python find_unit_price_quantity.py '{file_title}'")
os.system(f"python find_best_supplier.py '{file_title}'")
os.system(f"python combine_final_results.py '{file_title}'")


# os.system("python test_spider.py")
