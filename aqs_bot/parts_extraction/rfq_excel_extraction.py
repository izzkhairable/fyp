import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font
import pyodbc 
import os
import datetime

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

with open('aqs_bot/parts_extraction/config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for key, v in data.items():

        customerlist = cursor.execute("select * from dbo.customer where company_email=?", v['customer_email'])
        if len(customerlist.fetchall()) == 0:
            cursor.execute("insert into dbo.customer(company_email, company_name, company_website) values (?, ?, ?)", v['customer_email'], v['customer'], v['customer_website'])
            conn.commit()

        ## Scan Makino folder for RFQs and process each of them
        '''
        Code to be added here in future. below we asssuming we loop through one element
        '''

        selected_column_list = v['bom_column'].split(',')
        selected_column_list = [selected_column.lower().strip() for selected_column in selected_column_list] 
        wb = load_workbook('aqs_bot/parts_extraction/input/26VSMTC-0012-ST=15.xlsx')
        ws = wb['26VSMTC-0012-ST=14']
        
        check_if_quotation_exist = cursor.execute("select * from dbo.quotation where quotation_no=?", '26VSMTC-0012-ST=15')
        if len(check_if_quotation_exist.fetchall()) == 0:
            cursor.execute("insert into dbo.quotation(quotation_no, customer_email, assigned_staff_email, rfq_date, status) values (?, ?, ?, ?, ?)", '26VSMTC-0012-ST=15', v['customer_email'], 'darrenho.2019@scis.smu.edu.sg', datetime.datetime.now(), 'pending')
            conn.commit()
        
            start_row = 0
            selected_columns_index_list = []
            confirmed_columns_list = []

            part_no_col_index = None
            description_col_index = None
            qty_col_index = None
            uom_col_index = None
            price_col_index = None

            start_row = 0
            current_row_no = 1
            for row in ws.rows:
                current_col_no = 0
                if start_row != 0:
                    break
                for col in row:
                    if str(col.value).lower().strip() in selected_column_list:
                        selected_columns_index_list.append([current_row_no, current_col_no])
                        start_row = current_row_no
                    if str(col.value).lower().strip() == v['db_col_mapping']['part_no'].lower():
                        part_no_col_index = current_col_no
                    if str(col.value).lower().strip() == v['db_col_mapping']['description'].lower():
                        description_col_index = current_col_no
                    if str(col.value).lower().strip() == v['db_col_mapping']['qty'].lower():
                        qty_col_index = current_col_no
                    if str(col.value).lower().strip() == v['db_col_mapping']['uom'].lower():
                        uom_col_index = current_col_no
                    if str(col.value).lower().strip() == v['db_col_mapping']['price'].lower():
                        price_col_index = current_col_no
                    current_col_no+=1
                current_row_no+=1
            
            current_row_no = 1
            curr_set = None

            drawing_list = os.listdir('aqs_bot/parts_extraction/input')

            for row in ws.rows:
                drawing_found = False
                if start_row < current_row_no:
                    part_no = row[part_no_col_index].value
                    description = row[description_col_index].value
                    qty = row[qty_col_index].value
                    uom = row[uom_col_index].value
                    price = row[price_col_index].value
                    if row[uom_col_index].value == "SET":
                        curr_set = part_no
                        cursor.execute("insert into dbo.quotation_component(quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                '26VSMTC-0012-ST=15', part_no, uom, description, qty, price, 0, None, curr_set)
                        conn.commit()
                    else:
                        drawing_found = False
                        for file in drawing_list:
                            if part_no in file:
                                drawing_found = True
                                #open the file. insert each row into the drawing_parts table     
                                wb2 = load_workbook('aqs_bot/parts_extraction/input/' + file)
                                ws2 = wb2['Sheet1']
                                row_no = 1
                                for row in ws2.rows:
                                    if 1 < row_no:
                                        drawing_part_description = row[0].value
                                        drawing_part_no = row[1].value
                                        drawing_part_uom = row[4].value
                                        drawing_part_qty = row[5].value
                                        cursor.execute("insert into dbo.quotation_component(quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                '26VSMTC-0012-ST=15', drawing_part_no, drawing_part_uom, drawing_part_description, drawing_part_qty, None, 0, part_no, curr_set)
                                        conn.commit()
                                    row_no+=1
                        if drawing_found == False:
                            cursor.execute("insert into dbo.quotation_component(quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                '26VSMTC-0012-ST=15', part_no, uom, description, qty, price, 0, None, curr_set)
                            conn.commit()            
                current_row_no+=1     
conn.close()
print("Connection closed.")