from docx import Document
from docx.shared import Inches
import pyodbc
import json
import configparser

config = configparser.ConfigParser()
config.read('sql_connect.cfg')

conn = pyodbc.connect('Driver=' + config['database']['driver'] + ';'
                      'Server=' + config['database']['server'] + ';'
                      'Database=' + config['database']['database'] + ';'
                      'Trusted_Connection=' + config['database']['trusted_connection'] + ';')
cursor = conn.cursor()


quotation = cursor.execute(
    "select labour_cost, labour_no_of_hours, markup_pct, remark from dbo.quotation where quotation_no=?", 'quotation_one')
res = quotation.fetchone()

markup_pct = None
if res.markup_pct != None:
    markup_pct = res.markup_pct/100


row_level = cursor.execute(
    "select id, row, component_no, description, quantity, uom, unit_price, remark, crawl_info, bom_id from dbo.quotation_component where quotation_no=? ORDER BY row ASC", 'quotation_one')
result = row_level.fetchall()

total_price = 0

for each_row in result:
    unit_price = 0
    qty = 0
    if each_row.unit_price != None:
        unit_price = each_row.unit_price
    if each_row.quantity != None:
        qty = each_row.quantity
    price = unit_price * qty
    total_price+=price
    

print(total_price)
total_price = (total_price * markup_pct) + total_price + (res.labour_cost * res.labour_no_of_hours)

document = Document('aqs_bot/quotation_generation/Official Quotation Template.docx')

# print(document.tables[1].cell(0,1).text)

table = document.tables[2]
sn = 1
row = table.add_row().cells#https://github.com/python-openxml/python-docx/issues/205
row[0].text = str(sn)
row[1].text = "quotation_one"
row[3].text = "1"
row[4].text = "SET"
row[5].text = str(total_price)
row[6].text = str(total_price)


document.save('aqs_bot/quotation_generation/baby.docx')