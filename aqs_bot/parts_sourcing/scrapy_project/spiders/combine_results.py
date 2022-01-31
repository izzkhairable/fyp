import sys
import json
import os


def combine_results(file_title):
    # Need to make this dynamic instead of declaring variable
    parts = []
    mouser = []
    digikey = []
    rsonline = []
    element14 = []
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../input",
            f"{file_title}.json",
        )
    ) as parts_raw:
        try:
            parts = json.load(parts_raw)
        except:
            print("An exception occurred")
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_digikey_scrapped_data.json",
        )
    ) as digikey_raw:
        try:
            digikey = json.load(digikey_raw)
        except:
            print("An exception occurred")

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_mouser_scrapped_data.json",
        )
    ) as mouser_raw:
        try:
            mouser = json.load(mouser_raw)
        except:
            print("An exception occurred")

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_rsonline_scrapped_data.json",
        )
    ) as rsonline_raw:
        try:
            rsonline = json.load(rsonline_raw)
        except:
            print("An exception occurred")

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_element14_scrapped_data.json",
        )
    ) as element14_raw:
        try:
            element14 = json.load(element14_raw)
        except:
            print("An exception occurred")

    for part in parts["quotation_component"]:
        part["supplier"] = {}
        for scrapped_data in digikey:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"]["digikey.sg"] = scrapped_data
        for scrapped_data in mouser:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"]["mouser.sg"] = scrapped_data
        for scrapped_data in rsonline:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"]["sg.rs-online.com"] = scrapped_data
        for scrapped_data in element14:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"]["sg.element14.com"] = scrapped_data

    with open(f"../../output/{file_title}_combined_result.json", "w") as fp:
        json.dump(parts, fp)


if __name__ == "__main__":
    combine_results(sys.argv[1])
