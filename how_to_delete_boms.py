import pyodbc

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

## DELETE ITEM 4...
cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND component_no=?", 'quotation_one', 'bom_a')
conn.commit()


## ONCE ITEM 4 IS DELETED, ADD IT TO THE ARRAY
deleted_components = ['bom_a']

## RETRIEVE ALL COMPONENTS FOR THE CURRENT QUOTATION
row_level = cursor.execute(
    "select row, component_no, description, quantity, uom, unit_price, remark, crawl_info, bom_no from dbo.quotation_component where quotation_no=? ORDER BY ROW ASC", 'quotation_one')
result = row_level.fetchall()

## LOOP THROUGH EACH COMPONENTS, CHECK IF BOM_NO IS IN THE DELETED_COMPONENTS LIST. IF IT IS FOUND. IT MEANS IT  BELONGS TO THE BOM WE JUST DELETED, THEREFORE WE DELETE THIS COMPONENT TOO :)
for i in result:
    if i.bom_no in deleted_components:
        deleted_components.append(i.component_no)
        cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no=? AND component_no=?", 'quotation_one', i.component_no)
        conn.commit()

print("ok")