import pyodbc
import time
import math
start_time = time.time()

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()


get_bom = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE quotation_no=? AND id=?", 'quotation_one', 4)
result = get_bom.fetchone()

bom_id = result.id
bom_lvl = math.ceil(result.lvl)
bom_row = result.row
insert_to = bom_row+1



'''Now fix the row numberin '''
row_level = cursor.execute(
    "select id, row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_id, remark, crawl_info from dbo.quotation_component where quotation_no=? and row >= ? ORDER BY ROW ASC", 'quotation_one', insert_to)
result = row_level.fetchall()
row_no = insert_to+1
for i in result:
    cursor.execute("UPDATE dbo.quotation_component SET row=? WHERE quotation_no=? AND id=?", row_no, 'quotation_one', i.id)
    conn.commit()
    row_no+=1
print("--- %s seconds ---" % (time.time() - start_time))



'''NOW INSERT!'''
cursor.execute("insert into dbo.quotation_component(row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
insert_to, 'quotation_one', 'new_inserted_component', bom_lvl+1, 'EA', 'new component description', '1', None, 0, bom_id)
conn.commit()