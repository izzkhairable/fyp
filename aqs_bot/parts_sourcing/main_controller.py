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
        print(f"_____________Running {function_dir} Function____________")
        os.system(f"python {function_dir}.py {file_title}")

    if bot_config["settings"]["delete_input_outputs_after_uploaded"] == True:
        print(f"_____________Deleting Input Files____________")
        os.system(f"DEL .\input\{file_title}.json")
        print(f"_____________Deleting Output Files____________")
        os.system(f"DEL .\output\{file_title}_*.json")

    print(f"End of {file_title} part sourcing bot process")
