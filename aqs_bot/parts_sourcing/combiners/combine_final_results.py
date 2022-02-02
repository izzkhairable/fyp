import sys
import json
import os


def combine_results(file_title):
    # Need to make this dynamic instead of declaring variable
    parts = []
    misumi = []
    harting = []
    schneider = []
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../output",
            f"{file_title}_best_supplier_result.json",
        )
    ) as parts_raw:
        parts = json.load(parts_raw)

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../output",
            f"{file_title}_misumi_scrapped_data.json",
        )
    ) as misumi_raw:
        try:
            misumi = json.load(misumi_raw)
        except:
            print("An exception occurred")

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../output",
            f"{file_title}_harting_scrapped_data.json",
        )
    ) as harting_raw:
        try:
            harting = json.load(harting_raw)
        except:
            print("An exception occurred")

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../output",
            f"{file_title}_schneider_scrapped_data.json",
        )
    ) as schneider_raw:
        try:
            schneider = json.load(schneider_raw)
        except:
            print("An exception occurred")

    for part in parts["quotation_component"]:
        for scrapped_data in misumi:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"] = {
                    **part["supplier"],
                    "sg.misumi-ec.com": scrapped_data,
                }
        for scrapped_data in schneider:
            if part["mfg_pn"] == scrapped_data["mfg_pn"]:
                part["supplier"] = {**part["supplier"], "se.com": scrapped_data}
        for scrapped_data in harting:
            if part["mfg_pn"].replace(" ", "") == scrapped_data["mfg_pn"].replace(
                " ", ""
            ):
                part["supplier"] = {
                    **part["supplier"],
                    "b2b.harting.com": scrapped_data,
                }

    with open(f"./output/{file_title}_combined_final_result.json", "w") as fp:
        json.dump(parts, fp)


if __name__ == "__main__":
    combine_results(sys.argv[1])
