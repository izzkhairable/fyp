import sys
import json
import os
import math


def find_total_price_quantity(file_title):
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_combined_result.json",
        )
    ) as parts_raw:
        try:
            parts = json.load(parts_raw)
        except:
            print("An exception occurred")

    for part in parts["quotation_component"]:
        if len(part["supplier"]) > 0:
            supplier_name_list = list(part["supplier"].keys())
            cnt_non_mix_match = 0
            for supplier_name in supplier_name_list:
                supplier = part["supplier"][supplier_name]

                if (
                    part["UOM"] == "EA"
                    and supplier["quantity_available"] >= part["quantity"]
                ):
                    cnt_non_mix_match += 1
                    for price_row in supplier["pricing_table"]:
                        if (
                            part["quantity"] >= price_row["min_quantity"]
                            and part["quantity"] <= price_row["max_quantity"]
                        ):
                            supplier["total_price"] = (
                                price_row["unit_price"] * part["quantity"]
                            )
                            supplier["quantity_by_supplier"] = part["quantity"]

                elif part["UOM"] == "EA" and supplier["quantity_available"] > 0:
                    print("I am EA with lesser than need", part)
                    for price_row in supplier["pricing_table"]:
                        if (
                            part["quantity"] >= price_row["min_quantity"]
                            and part["quantity"] <= price_row["max_quantity"]
                        ):
                            supplier["total_price"] = (
                                price_row["unit_price"] * supplier["quantity_available"]
                            )
                            supplier["quantity_by_supplier"] = supplier[
                                "quantity_available"
                            ]

                if (
                    part["UOM"] == "M"
                    and supplier["quantity_available"] * supplier["selling_length"]
                    >= part["quantity"]
                ):
                    cnt_non_mix_match += 1
                    quantity_needed = math.ceil(
                        part["quantity"] / supplier["selling_length"]
                    )
                    # print("This is part", part)
                    for price_row in supplier["pricing_table"]:
                        if (
                            part["quantity"] >= price_row["min_quantity"]
                            and part["quantity"] <= price_row["max_quantity"]
                        ):
                            supplier["total_price"] = (
                                price_row["unit_price"] * quantity_needed
                            )
                            supplier["quantity_by_supplier"] = quantity_needed
                elif part["UOM"] == "M" and supplier["quantity_available"] > 0:
                    # print("This is part", part)
                    print("I am M with lesser than need", part)
                    for price_row in supplier["pricing_table"]:
                        if (
                            part["quantity"] >= price_row["min_quantity"]
                            and part["quantity"] <= price_row["max_quantity"]
                        ):
                            supplier["total_price"] = (
                                price_row["unit_price"] * supplier["quantity_available"]
                            )
                            supplier["quantity_by_supplier"] = supplier[
                                "quantity_available"
                            ]

                if (
                    "total_price" not in supplier
                    and "quantity_by_supplier" not in supplier
                ):
                    supplier["total_price"] = None
                    supplier["quantity_by_supplier"] = None
            if cnt_non_mix_match < 1:
                part["mix_match"] = True
            else:
                part["mix_match"] = False

    with open(f"../../output/{file_title}_total_price_quantity_result.json", "w") as fp:
        json.dump(parts, fp)


if __name__ == "__main__":
    find_total_price_quantity(sys.argv[1])
