import sys
import json
import os
import math


def find_best_supplier(file_title):
    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../../output",
            f"{file_title}_total_price_quantity_result.json",
        )
    ) as parts_raw:
        try:
            parts = json.load(parts_raw)
        except:
            print("An exception occurred")

    for part in parts["quotation_component"]:
        if len(part["supplier"]) > 0:
            if part["mix_match"] == False:
                supplier_name_list = list(part["supplier"].keys())
                best_total_price = float("inf")
                best_supplier = None
                for supplier_name in supplier_name_list:
                    total_price = part["supplier"][supplier_name]["total_price"]
                    quantity_by_supplier = part["supplier"][supplier_name][
                        "quantity_by_supplier"
                    ]
                    if (
                        total_price != None
                        and quantity_by_supplier != None
                        and total_price <= best_total_price
                    ):
                        best_total_price = total_price
                        best_supplier = supplier_name

                if best_supplier != None:
                    part["supplier"] = {best_supplier: part["supplier"][best_supplier]}
                    part["total_price"] = total_price
                else:
                    part["supplier"] = {}
            else:

                supplier_name_list = list(part["supplier"].keys())
                supplier_unit_price_list = []
                for supplier_name in supplier_name_list:
                    if part["UOM"] == "EA":
                        total_price = part["supplier"][supplier_name]["total_price"]
                        quantity_by_supplier = part["supplier"][supplier_name][
                            "quantity_by_supplier"
                        ]
                        unit_price = total_price / quantity_by_supplier
                        supplier_unit_price_list.append(
                            {"supplier_name": supplier_name, "unit_price": unit_price}
                        )
                    if part["UOM"] == "M":
                        total_price = part["supplier"][supplier_name]["total_price"]
                        quantity_by_supplier = part["supplier"][supplier_name][
                            "quantity_by_supplier"
                        ]
                        price_per_meter = (total_price / quantity_by_supplier) / part[
                            "supplier"
                        ][supplier_name]["selling_length"]
                        supplier_unit_price_list.append(
                            {
                                "supplier_name": supplier_name,
                                "unit_price": price_per_meter,
                            }
                        )

                supplier_unit_price_list = list(
                    sorted(supplier_unit_price_list, key=lambda d: d["unit_price"]),
                )
                print("part me", part)
                print(supplier_unit_price_list)
                quantity_remaining = part["quantity"]
                best_supplier_list = {}
                for idx in range(len(supplier_unit_price_list)):

                    supplier_name = supplier_unit_price_list[idx]["supplier_name"]
                    quantity_available = part["supplier"][supplier_name][
                        "quantity_available"
                    ]

                    if part["UOM"] == "EA" and quantity_remaining > 0:

                        quantity_by_supplier = part["supplier"][supplier_name][
                            "quantity_by_supplier"
                        ]
                        best_supplier_list[supplier_name] = part["supplier"][
                            supplier_name
                        ]
                        # 5                     6
                        if quantity_remaining >= quantity_available:
                            print("im in here where more", supplier_name)
                            quantity_remaining = quantity_remaining - quantity_available
                            # 5                     10
                        elif quantity_remaining < quantity_available:
                            print("im in here where lesser", supplier_name)
                            part["supplier"][supplier_name][
                                "quantity_by_supplier"
                            ] = quantity_remaining
                            part["supplier"][supplier_name]["total_price"] = (
                                quantity_remaining * unit_price
                            )
                            quantity_remaining = 0

                    elif part["UOM"] == "M" and quantity_remaining > 0:
                        quantity_by_supplier = part["supplier"][supplier_name][
                            "quantity_by_supplier"
                        ]
                        selling_length = part["supplier"][supplier_name][
                            "selling_length"
                        ]
                        best_supplier_list[supplier_name] = part["supplier"][
                            supplier_name
                        ]
                        # 5                     6
                        if quantity_remaining >= quantity_available * selling_length:
                            print("im in here where more", supplier_name)
                            quantity_remaining = quantity_remaining - (
                                quantity_available * selling_length
                            )
                            # 5                     10
                        elif quantity_remaining < quantity_available * selling_length:
                            print("im in here where lesser", supplier_name)
                            part["supplier"][supplier_name][
                                "quantity_by_supplier"
                            ] = math.ceil(quantity_remaining / selling_length)
                            part["supplier"][supplier_name]["total_price"] = (
                                math.ceil(quantity_remaining / selling_length)
                                * unit_price
                            )
                            quantity_remaining = 0
                    print(quantity_available, quantity_remaining)
                part["supplier"] = best_supplier_list
    with open(f"../../output/{file_title}_best_supplier_result.json", "w") as fp:
        json.dump(parts, fp)


if __name__ == "__main__":
    find_best_supplier(sys.argv[1])
