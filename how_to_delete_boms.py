import pyodbc
import time
start_time = time.time()

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

## DELETE ITEM 4...
cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND component_no=?", 'rfqsample', '26VS691A-01.8')
conn.commit()


## ONCE ITEM 4 IS DELETED, ADD IT TO THE ARRAY
deleted_components = ['26VS691A-01.8']

## RETRIEVE ALL COMPONENTS FOR THE CURRENT QUOTATION
row_level = cursor.execute(
    "select row, component_no, description, quantity, uom, unit_price, remark, crawl_info, bom_no from dbo.quotation_component where quotation_no=? ORDER BY ROW ASC", 'rfqsample')
result = row_level.fetchall()

## LOOP THROUGH EACH COMPONENTS, CHECK IF BOM_NO IS IN THE DELETED_COMPONENTS LIST. IF IT IS FOUND. IT MEANS IT  BELONGS TO THE BOM WE JUST DELETED, THEREFORE WE DELETE THIS COMPONENT TOO :)
for i in result:
    if i.bom_no in deleted_components:
        deleted_components.append(i.component_no)
        cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND component_no=?", 'rfqsample', i.component_no)
        conn.commit()


'''Now fix the row numberin '''
row_level = cursor.execute(
    "select row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_no, remark, crawl_info from dbo.quotation_component where quotation_no=? ORDER BY ROW ASC", 'rfqsample')
result = row_level.fetchall()

row_no = 1
for i in result:
    cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND row=?", 'rfqsample', i.row)
    conn.commit()
    cursor.execute("INSERT INTO dbo.quotation_component (row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_no, remark, crawl_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
    row_no, i.quotation_no, i.component_no, i.lvl, i.uom, i.description, i.quantity, i.unit_price, i.is_bom, i.bom_no, i.remark, i.crawl_info)
    conn.commit()
    row_no+=1
print("--- %s seconds ---" % (time.time() - start_time))
