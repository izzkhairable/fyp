def string_cleaning(str):
    return (
        str.replace("/r", "")
        .replace("/n", "")
        .replace("\r", "")
        .replace("\n", "")
        .strip()
    )


def get_part_requirements(parts, raw_mfg_pn):
    print("Current raw_mfg_pn", raw_mfg_pn)
    mfg_pn = string_cleaning(raw_mfg_pn.lower())
    print("Current mfg_pn", mfg_pn)
    for part in parts:
        print(
            "for parts and raw_mfg_pn",
            string_cleaning(part["MFG PN."].lower()),
            mfg_pn,
        )
        if string_cleaning(part["MFG PN."].lower()) == mfg_pn:
            print(
                "If parts and raw_mfg_pn",
                string_cleaning(part["MFG PN."].lower()),
                mfg_pn,
            )
            return part


def validate_part_brand(raw_manufacturer_brand, description):
    if (
        description != ""
        and description.find(string_cleaning(raw_manufacturer_brand.lower())) != -1
    ):
        return True
    elif (
        string_cleaning(raw_manufacturer_brand.lower()).find("te connectivity") != -1
        and description.find("faston 250") != -1
    ):
        return True
    else:
        return False


def validate_quantity_available(quantity_available, quantity_needed, uom):
    quantity_available = quantity_available
    quantity_needed = int(quantity_needed)
    if quantity_available < 1:
        return False
    else:
        return True
