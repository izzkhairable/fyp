import os
import sys
import json
import pyodbc
import configparser


def quotation_uploader(file_title):
    config = configparser.ConfigParser()
    config.read("../../sql_connect.cfg")

    conn = pyodbc.connect(
        "Driver=" + config["database"]["driver"] + ";"
        "Server=" + config["database"]["server"] + ";"
        "Database=" + config["database"]["database"] + ";"
        "Trusted_Connection=" + config["database"]["trusted_connection"] + ";"
    )

    with open(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..\output",
            f"{file_title}_combined_final_result.json",
        )
    ) as combined_final_raw:
        try:
            combined_final = json.load(combined_final_raw)
        except:
            print("An exception occurred")

    for part in combined_final["quotation_component"]:
        supplier_name_list = list(part["supplier"].keys())
        total_unit_price = 0
        total_num_suppliers = 0
        total_quantity = 0
        supplier_list = []
        for supplier_name in supplier_name_list:
            supplier_dict = part["supplier"][supplier_name]
            quantity_by_supplier = None
            unit_price = None
            if (
                "unit_price" in supplier_dict
                and "quantity_by_supplier" in supplier_dict
            ):
                quantity_by_supplier = supplier_dict["quantity_by_supplier"]
                unit_price = supplier_dict["unit_price"]
            supplier_list.append(
                {
                    "supplier": supplier_name,
                    "url": part["supplier"][supplier_name]["url"],
                    "qty": quantity_by_supplier,
                    "unit_price": unit_price,
                }
            )
            if supplier_name not in ["sg.misumi-ec.com", "se.com", "b2b.harting.com"]:
                total_unit_price += part["supplier"][supplier_name]["unit_price"]
                total_num_suppliers += 1
                if part["UOM"] == "EA":
                    total_quantity += part["supplier"][supplier_name][
                        "quantity_by_supplier"
                    ]
                elif part["UOM"] == "M":
                    total_quantity += (
                        part["supplier"][supplier_name]["quantity_by_supplier"]
                        * part["supplier"][supplier_name]["selling_length"]
                    )

        supplier_list_str = json.dumps(supplier_list)
        print(supplier_list_str)
        average_unit_price = 0
        if total_unit_price > 0 and total_num_suppliers > 0:
            average_unit_price = total_unit_price / total_num_suppliers
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE dbo.quotation_component SET crawl_info  = '{supplier_list_str}', unit_price='{average_unit_price}', quantity={total_quantity} WHERE component_no ='{part['component_no']}' AND row='{part['row']}';"
        )
        conn.commit()
    for part in combined_final["quotation_component_consignment"]:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE dbo.quotation_component SET unit_price='0' WHERE component_no ='{part['component_no']}' AND row='{part['row']}';"
        )
        conn.commit()
    for part in combined_final["quotation_component_fixed_supplier"]:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE dbo.quotation_component SET unit_price='{part['unit_price']}' WHERE component_no ='{part['component_no']}' AND row='{part['row']}';"
        )
        conn.commit()

    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE dbo.quotation SET status='scraped' WHERE quotation_no ='{file_title}';"
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    quotation_uploader(sys.argv[1])
