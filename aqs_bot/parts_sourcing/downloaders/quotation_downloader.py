from calendar import month
import pyodbc
import pandas as pd
import json
import math
import configparser
from datetime import datetime
import yaml

config = configparser.ConfigParser()
config.read("../../sql_connect.cfg")

conn = pyodbc.connect(
    "Driver=" + config["database"]["driver"] + ";"
    "Server=" + config["database"]["server"] + ";"
    "Database=" + config["database"]["database"] + ";"
    "Trusted_Connection=" + config["database"]["trusted_connection"] + ";"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM dbo.quotation WHERE status='draft'")


with open("./config.yaml") as file:
    bot_config = yaml.load(file, Loader=yaml.FullLoader)
    max_duration_raw = bot_config["item_master_price"]["max_duration_since_updated"]
    duration_unit = bot_config["item_master_price"]["duration_unit"]
    max_duration = 0
    if duration_unit == "months":
        max_duration = max_duration_raw * 30.437
    elif duration_unit == "years":
        max_duration = max_duration_raw * 365.25
    else:
        max_duration = max_duration_raw


def retrieve_all_draft_quotations():
    draft_quotation_list = []
    for i in cursor:
        one_quotation_list = list(i)
        quotation_dict = {
            "quotation_no": one_quotation_list[0],
            "customer": one_quotation_list[1],
            "assigned_staff": one_quotation_list[2],
        }
        draft_quotation_list.append(quotation_dict)
    return draft_quotation_list


def retrieve_all_items_in_quotation(draft_quotation_list):
    for quotation in draft_quotation_list:
        draft_quotation_item_list = []
        draft_quotation_item_list_consignment = []
        draft_quotation_item_list_fixed_supplier = []
        cursor.execute(
            f"SELECT * FROM dbo.quotation_component WHERE quotation_no='{quotation['quotation_no']}' AND (uom='EA' OR uom='M')"
        )

        for i in cursor:
            one_quotation_item_list = list(i)
            quotation_item_dict = {
                "row": one_quotation_item_list[2],
                "component_no": one_quotation_item_list[3],
                "UOM": one_quotation_item_list[5],
                "description": one_quotation_item_list[6],
                "quantity": one_quotation_item_list[7],
                "customer_id": one_quotation_item_list[1],
            }

            library_component_dict = find_in_item_mater(
                quotation_item_dict["component_no"]
            )

            company_name = find_company_name(quotation["customer"])

            if library_component_dict == None:
                quotation_item_dict["mfg_pn"] = quotation_item_dict["description"]
                quotation_item_dict["found_in_item_master"] = False
                draft_quotation_item_list.append(quotation_item_dict)
            else:
                quotation_item_dict["found_in_item_master"] = True
                if (
                    library_component_dict["type"] == "standard"
                    and library_component_dict["to_be_updated"] == True
                ):
                    quotation_item_dict["mfg_pn"] = str(
                        library_component_dict["mfg_pn"]
                    )
                    draft_quotation_item_list.append(quotation_item_dict)
                elif (
                    library_component_dict["type"] == "consignment"
                    and library_component_dict["supplier"] == company_name
                    and library_component_dict["unit_price"] == 0
                ):
                    quotation_item_dict["mfg_pn"] = library_component_dict["mfg_pn"]
                    draft_quotation_item_list_consignment.append(quotation_item_dict)
                else:
                    quotation_item_dict["mfg_pn"] = library_component_dict["mfg_pn"]
                    quotation_item_dict["unit_price"] = library_component_dict[
                        "unit_price"
                    ]
                    quotation_item_dict["supplier"] = library_component_dict["supplier"]
                    draft_quotation_item_list_fixed_supplier.append(quotation_item_dict)

        quotation["quotation_component"] = draft_quotation_item_list
        quotation[
            "quotation_component_consignment"
        ] = draft_quotation_item_list_consignment
        quotation[
            "quotation_component_fixed_supplier"
        ] = draft_quotation_item_list_fixed_supplier

    return draft_quotation_list


def save_quotation_and_items_to_json(draft_quotation_list):
    file_titles = []
    for quotation in draft_quotation_list:
        with open(f"./input/{quotation['quotation_no']}.json", "w") as fp:
            json.dump(quotation, fp)
        file_titles.append(quotation["quotation_no"])
    return file_titles


def find_in_item_mater(component_no):
    conn_minor = pyodbc.connect(
        "Driver=" + config["database"]["driver"] + ";"
        "Server=" + config["database"]["server"] + ";"
        "Database=" + config["database"]["database"] + ";"
        "Trusted_Connection=" + config["database"]["trusted_connection"] + ";"
    )
    cursor_minor = conn_minor.cursor()
    cursor_minor.execute(
        f"SELECT * FROM dbo.item_master WHERE component_no='{component_no}'"
    )
    item_tuple = cursor_minor.fetchone()
    if item_tuple != None:
        item_list = list(item_tuple)
        item_dict = {
            "unit_price": item_list[1],
            "mfg_pn": item_list[3],
            "supplier": item_list[5],
            "type": item_list[4],
            "last_updated": item_list[7],
        }

        diff_delta = datetime.now() - item_dict["last_updated"]
        if diff_delta.days > max_duration:
            item_dict["to_be_updated"] = True

        else:
            item_dict["to_be_updated"] = False

        conn_minor.close()
        return item_dict
    else:
        conn_minor.close()
        return None


def find_company_name(customer_id):
    conn_minor = pyodbc.connect(
        "Driver=" + config["database"]["driver"] + ";"
        "Server=" + config["database"]["server"] + ";"
        "Database=" + config["database"]["database"] + ";"
        "Trusted_Connection=" + config["database"]["trusted_connection"] + ";"
    )
    cursor_minor = conn_minor.cursor()
    cursor_minor.execute(f"SELECT * FROM dbo.customer WHERE id={customer_id}")
    item_tuple = cursor_minor.fetchone()
    if item_tuple != None:
        company_name = item_tuple[1]
        conn_minor.close()
        print("This is company name", company_name)
        return company_name
    else:
        conn_minor.close()
        return None


def quotation_downloader():
    draft_quotation_list = retrieve_all_draft_quotations()
    draft_quotation_list_with_item = retrieve_all_items_in_quotation(
        draft_quotation_list
    )
    if draft_quotation_list_with_item != None:
        file_titles = save_quotation_and_items_to_json(draft_quotation_list_with_item)
        conn.close()
        return file_titles
