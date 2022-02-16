from tkinter.tix import Tree


def string_cleaning(str):
    return (
        str.replace("/r", "")
        .replace("/n", "")
        .replace("\r", "")
        .replace("\n", "")
        .strip()
    )


def get_part_requirements(parts, url, supplier_domain):
    print("I am in get_part_requirements", parts, url, supplier_domain)
    for part in parts:
        if supplier_domain in part["supplier_links"]:
            if (
                part["supplier_links"][supplier_domain][0]
                == url
            ):
                print("This is the item found", part["item"])
                return part["item"]


def get_part_requirements_google(parts, raw_mfg_pn):
    mfg_pn = string_cleaning(raw_mfg_pn.lower())
    for part in parts["quotation_component"]:
        if string_cleaning(part["mfg_pn"].lower()) == mfg_pn:
            return part


def validate_part_brand(raw_manufacturer_brand, description):
    # if (
    #     description != ""
    #     and description.find(string_cleaning(raw_manufacturer_brand.lower())) != -1
    # ):
    #     return True
    # elif (
    #     string_cleaning(raw_manufacturer_brand.lower()).find("te connectivity") != -1
    #     and description.find("faston 250") != -1
    # ):
    #     return True
    # else:
    #     return False
    return True


def validate_quantity_available(quantity_available, quantity_needed, uom):
    quantity_available = quantity_available
    quantity_needed = int(quantity_needed)
    if quantity_available < 1:
        return False
    else:
        return True


def get_selling_length(description, supplier):
    description = string_cleaning(description.lower())
    if supplier == "digikey.sg":
        start_pos = description.rfind("(") + 1
        end_pos = description.rfind("m)")
        return float(description[start_pos:end_pos])
    elif supplier == "sg.rs-online.com":
        description_arr = description.split(", ")
        for sub in description_arr:
            if sub.replace(" ", "").replace("m", "").isnumeric():
                return float(sub.replace(" ", "").replace("m", ""))
            elif sub.replace(" ", "").replace("m", "").replace("l", "").isnumeric():
                return float(sub.replace(" ", "").replace("m", "").replace("l", ""))
    elif supplier == "sg.element14.com":
        description_arr = description.split(", ")
        for sub in description_arr:
            if sub.replace(" ", "").replace("m", "").isnumeric():
                return float(sub.replace(" ", "").replace("m", ""))
    elif supplier == "mouser.sg":
        description_arr = description.split(" ")
        if (
            description.find("sold by foot") != -1
            or description.find("price per foot") != -1
            or description.find("sold per foot") != -1
        ):
            return 1.0 / 3.281
        elif (
            description.find("sold in mtrs") != -1
            or description.find("price per meter") != -1
            or description.find("price per m") != -1
            or description.find("priced per meter") != -1
        ):
            return 1.0
        for idx, sub in enumerate(description_arr):
            if sub.isnumeric():
                if (
                    description_arr[idx + 1] == "meter"
                    or description_arr[idx + 1] == "meters"
                ):
                    return float(sub)
                elif description_arr[idx + 1] == "FT/REEL":
                    return float(sub) / 3.281
            if sub.replace("ft", "").isnumeric():
                return float(sub.replace("ft", "")) / 3.281
