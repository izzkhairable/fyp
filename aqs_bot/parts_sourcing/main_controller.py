import os
import sys
from downloaders.quotation_downloader import quotation_downloader
import yaml

file_titles = quotation_downloader()
with open("./config.yaml") as file:
    bot_config = yaml.load(file, Loader=yaml.FullLoader)

for file_title in file_titles:
    print("_____________Running Google Spider____________")
    os.system(f"python ./scrapers/spiders/google_search_spider.py {file_title}")

    for supplier in bot_config["to_run"]["suppliers_spiders"]:
        print(f"_____________Running {supplier} Spider____________")
        os.system(f"python ./scrapers/spiders/{supplier}.py {file_title}")
    for function_dir in bot_config["to_run"]["sequential_functions"]:
        print("_____________Running Combine Results Function____________")
        os.system(f"python {function_dir}.py {file_title}")

    print(f"End of {file_title} part sourcing bot process")
