import pyodbc
import pandas as pd
import json
import math

conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP-TK0O9CKS;"
    "Database=myerp101;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM dbo.quotation WHERE status='draft'")
df = pd.read_excel("./input/component_library.xlsx")


def retrieve_all_draft_quotations():
    draft_quotation_list = []
    for i in cursor:
        one_quotation_list = list(i)
        quotation_dict = {
            "quotation_no": one_quotation_list[0],
            "customer_email": one_quotation_list[1],
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
                "row": one_quotation_item_list[0],
                "component_no": one_quotation_item_list[2],
                "UOM": one_quotation_item_list[4],
                "description": one_quotation_item_list[5],
                "quantity": one_quotation_item_list[6],
            }

            library_component_dict = (
                df.loc[df["Component number"] == quotation_item_dict["component_no"]]
                .iloc[[0]]
                .to_dict("r")[0]
            )

            if (
                library_component_dict["Type"] == "Standard"
                and isinstance(library_component_dict["Assigned Supplier"], float)
                and isinstance(library_component_dict["Unit Price"], float)
            ):
                quotation_item_dict["mfg_pn"] = str(library_component_dict["Mfg pn"])
                draft_quotation_item_list.append(quotation_item_dict)
            elif (
                library_component_dict["Type"] == "Consignment"
                and str(library_component_dict["Assigned Supplier"]) != ""
                and library_component_dict["Unit Price"] == 0
            ):
                quotation_item_dict["mfg_pn"] = library_component_dict["Mfg pn"]
                draft_quotation_item_list_consignment.append(quotation_item_dict)
            else:
                quotation_item_dict["mfg_pn"] = library_component_dict["Mfg pn"]
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


def quotation_downloader():
    draft_quotation_list = retrieve_all_draft_quotations()
    draft_quotation_list_with_item = retrieve_all_items_in_quotation(
        draft_quotation_list
    )
    file_titles = save_quotation_and_items_to_json(draft_quotation_list_with_item)
    return file_titles
