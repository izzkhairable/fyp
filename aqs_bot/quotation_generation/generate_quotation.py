from py import process
import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font, Border, Side, PatternFill, Font
import pyodbc 
import os
import pandas as pd
import datetime
import tabula
from pathlib import Path
import shutil
import sys
import json 

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
wb = Workbook()

ws = wb.active

ws.cell(row=1, column=1).value = "Row"
ws.cell(row=1, column=2).value = "Component Number"
ws.cell(row=1, column=3).value = "Object Description"
ws.cell(row=1, column=4).value = "Qty"
ws.cell(row=1, column=5).value = "Component unit"
ws.cell(row=1, column=6).value = "Price"
ws.cell(row=1, column=7).value = "Total"
ws.cell(row=1, column=8).value = "Remarks"

ws.cell(row=1, column=1).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=2).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=3).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=4).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=5).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=6).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=7).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")
ws.cell(row=1, column=8).fill = PatternFill(start_color='4BACC6', end_color='4BACC6', fill_type="solid")

ws.cell(row=1, column=1).font = Font(bold=True)
ws.cell(row=1, column=2).font = Font(bold=True)
ws.cell(row=1, column=3).font = Font(bold=True)
ws.cell(row=1, column=4).font = Font(bold=True)
ws.cell(row=1, column=5).font = Font(bold=True)
ws.cell(row=1, column=6).font = Font(bold=True)
ws.cell(row=1, column=7).font = Font(bold=True)
ws.cell(row=1, column=8).font = Font(bold=True)

row_level = cursor.execute(
    "select row, component_no, description, quantity, uom, unit_price, remark, crawl_info from dbo.quotation_component where quotation_no=?", 'quotation_one')
result = row_level.fetchall()

thin = Side(border_style="thin", color="000000")

row_no = 2
for each_row in result:
    ws.cell(row=row_no, column=1).value = each_row.row
    ws.cell(row=row_no, column=2).value = each_row.component_no
    ws.cell(row=row_no, column=3).value = each_row.description
    ws.cell(row=row_no, column=4).value = each_row.quantity
    ws.cell(row=row_no, column=5).value = each_row.uom
    ws.cell(row=row_no, column=6).value = each_row.unit_price
    ws.cell(row=row_no, column=7).value = 5555
    ws.cell(row=row_no, column=8).value = each_row.remark
    ws.cell(row=row_no, column=9).value = '=SUM(3,2)'

    ws.cell(row=row_no, column=1).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=2).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=3).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=4).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=5).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=6).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=7).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=8).border = Border(top=thin, left=thin, right=thin, bottom=thin)
    ws.cell(row=row_no, column=8).border = Border(top=thin, left=thin, right=thin, bottom=thin)

    row_no+=1

wb.save('document.xlsx')