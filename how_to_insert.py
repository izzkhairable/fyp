import pyodbc
import time
import math
start_time = time.time()

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS\SQLEXPRESS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


get_bom = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE id=?", 2)
result = get_bom.fetchone()
bom_id = result.id
bom_lvl = math.ceil(result.lvl)
bom_row = result.row
component_level_to_insert = bom_lvl+1

get_range = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE quotation_no=? AND row >= ? ORDER BY ROW", 'quotation_one', bom_row)
result = get_range.fetchall()


row_to_insert_new_item = None
for each_row in result:
    next_item = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE quotation_no=? AND row = ? ORDER BY ROW", 'quotation_one', each_row.row+1)
    res = get_range.fetchone()
    if res != None:
        if component_level_to_insert > res.lvl:
            row_to_insert_new_item = each_row.row+1
            break        
    else:
        row_to_insert_new_item = each_row.row+1


## Fix the rows before inserting ##
get_range = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE quotation_no=? AND row >= ? ORDER BY ROW", 'quotation_one', row_to_insert_new_item)
result = get_range.fetchall()

if len(result) > 0:
    for each_row in result:
        cursor.execute("UPDATE dbo.quotation_component SET row=? WHERE quotation_no=? AND id=?", each_row.row+1, 'quotation_one', each_row.id)
        conn.commit()


## Now let's insert the new item ##
cursor.execute("INSERT INTO dbo.quotation_component (quotation_no, row, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_id, remark, crawl_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 'quotation_one', row_to_insert_new_item, 'New component', component_level_to_insert, 'EA', 'New component description', 69, 1.50, 0, bom_id, 'no remarks', None)
conn.commit()

