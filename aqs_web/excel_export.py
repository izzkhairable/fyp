# pip install openpyxl

# data goes here (maybe json? yaml? see how)

import openpyxl

export_excel = openpyxl.workbook(path)
sheet = export_excel.active()

sheet.title = "Quotation #"

# fill data in sheet with json data exported from web app

export_excel.save(filename="RFQ #.xlsx")



