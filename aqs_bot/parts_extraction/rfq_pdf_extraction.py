# Import the required Module
import tabula
import pandas as pd
import os
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font
# convert PDF into CSV

tabula.convert_into(r'C:\Users\Darren Ho\Documents\GitHub\fyp\aqs_bot\parts_extraction\input\rfq\26VSMTC-0012-ST=14.pdf', "iplmatch.csv", output_format="csv", pages='all')
read_file = pd.read_csv(r'iplmatch.csv')
read_file.to_excel (r'omg.xlsx', index = None, header=True)
os.remove(r'iplmatch.csv')

wb = load_workbook(r'omg.xlsx')
ws = wb.worksheets[0]


records = []
for row in ws.rows:
    row_items = []
    for col in row:
        row_items.append(col.value)
    records.append(row_items)
    if len(records) > 1:
        if records[0] == row_items:
            print("ALERT")

