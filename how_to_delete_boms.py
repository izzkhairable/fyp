import pyodbc
import time
start_time = time.time()

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

## DELETE ITEM 4...
cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND id=?", 'testpdf', 188) #row 178 to 212
conn.commit()


## ONCE ITEM 4 IS DELETED, ADD IT TO THE ARRAY
deleted_components = [188]

## RETRIEVE ALL COMPONENTS FOR THE CURRENT QUOTATION
row_level = cursor.execute(
    "select id, row, component_no, description, quantity, uom, unit_price, remark, crawl_info, bom_id from dbo.quotation_component where quotation_no=? ORDER BY ROW ASC", 'testpdf')
result = row_level.fetchall()

## LOOP THROUGH EACH COMPONENTS, CHECK IF BOM_NO IS IN THE DELETED_COMPONENTS LIST. IF IT IS FOUND. IT MEANS IT  BELONGS TO THE BOM WE JUST DELETED, THEREFORE WE DELETE THIS COMPONENT TOO :)
for i in result:
    if i.bom_id in deleted_components:
        deleted_components.append(i.id)
        cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND id=?", 'testpdf', i.id)
        conn.commit()


'''Now fix the row numberin '''
row_level = cursor.execute(
    "select id, row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_id, remark, crawl_info from dbo.quotation_component where quotation_no=? ORDER BY ROW ASC", 'testpdf')
result = row_level.fetchall()

row_no = 1
for i in result:
    cursor.execute("UPDATE dbo.quotation_component SET row=? WHERE quotation_no=? AND id=?", row_no, 'testpdf', i.id)
    conn.commit()
    row_no+=1
print("--- %s seconds ---" % (time.time() - start_time))

