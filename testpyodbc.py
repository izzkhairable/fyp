import pyodbc

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

customerlist = cursor.execute("select lvl, row from dbo.quotation_component where row=?", 1563)
result = customerlist.fetchone()
print(result.lvl)
print(result.row)
