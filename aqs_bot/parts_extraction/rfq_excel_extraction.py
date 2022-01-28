from py import process
import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font
import pyodbc 
import os
import pandas as pd
import datetime
import tabula
from pathlib import Path
import shutil
import sys
def processPDF(filepath):
    print("Processing PDF...")
    tabula.convert_into(filepath, v['rfq_folder'] + '/' + rfq_number + ".csv", output_format="csv", pages='all')
    read_file = pd.read_csv(v['rfq_folder'] + '/' + rfq_number + ".csv")
    read_file.to_excel (v['rfq_folder'] + '/' + rfq_number + '_temp.xlsx', index = None, header=True)
    
    wb = load_workbook(v['rfq_folder'] + '/' + rfq_number + '_temp.xlsx')
    ws = wb.worksheets[0]
    records = []
    row_no = 1
    for row in ws.rows:
        row_items = []
        for col in row:
            row_items.append(col.value)
        records.append(row_items)
        if len(records) > 1:
            if records[0] == row_items:
                ws.delete_rows(row_no, 1)
        row_no+=1
    wb.save(v['rfq_folder'] + '/' + rfq_number + '_to_process.xlsx')
    processExcel(v['rfq_folder'] + '/' + rfq_number + '_to_process.xlsx')

    files_to_remove = [
        v['rfq_folder'] + '/' + rfq_number + ".csv",
        v['rfq_folder'] + '/' + rfq_number + '_temp.xlsx',
        v['rfq_folder'] + '/' + rfq_number + '_to_process.xlsx'
    ]
    for file in files_to_remove:
        os.remove(file)

def processExcel(filepath):
    print("Processing Excel")
    wb = load_workbook(filepath)
    ws = wb.worksheets[0]
                    
    start_row = 0
    part_no_col_index = None
    description_col_index = None
    qty_col_index = None
    uom_col_index = None

    part_no_col_list = v['rfq_to_db_mapping']['part_no'].split(',')
    part_no_col_list = [selected_column.lower().strip() for selected_column in part_no_col_list] 

    description_col_list = v['rfq_to_db_mapping']['description'].split(',')
    description_col_list = [selected_column.lower().strip() for selected_column in description_col_list] 

    qty_list = v['rfq_to_db_mapping']['qty'].split(',')
    qty_list = [selected_column.lower().strip() for selected_column in qty_list] 
    
    uom_col_list = v['rfq_to_db_mapping']['uom'].split(',')
    uom_col_list = [selected_column.lower().strip() for selected_column in uom_col_list] 

    all_col_list = part_no_col_list + description_col_list + qty_list + uom_col_list

    start_row_list = []
    current_row_no = 1
    for row in ws.rows:
        for col in row:
            if str(col.value).lower().strip() in all_col_list:
                start_row_list.append(current_row_no)
        current_row_no+=1
    
    if len(start_row_list) != 0:
        check_if_quotation_exist = cursor.execute("select * from dbo.quotation where quotation_no=?", rfq_number)
        if len(check_if_quotation_exist.fetchall()) == 0:
            cursor.execute("insert into dbo.quotation(quotation_no, customer_email, assigned_staff, rfq_date, status) values (?, ?, ?, ?, ?)", rfq_number, v['customer_email'], 2, datetime.datetime.now(), 'pending')
            conn.commit()
            start_row = max(set(start_row_list), key = start_row_list.count)    
            
            all_column_headers_in_excel = []
            for col_name in ws[start_row]:
                all_column_headers_in_excel.append(str(col_name.value).lower().strip())
            
            for part_no_col in part_no_col_list:
                try:
                    part_no_col_index = all_column_headers_in_excel.index(part_no_col)
                except ValueError as e:
                    pass
            for description_col in description_col_list:
                try:
                    description_col_index = all_column_headers_in_excel.index(description_col)
                except ValueError as e:
                    pass
            for qty_col in qty_list:
                try:
                    qty_col_index = all_column_headers_in_excel.index(qty_col)
                except ValueError as e:
                    pass
            for uom_col in uom_col_list:
                try:
                    uom_col_index = all_column_headers_in_excel.index(uom_col)
                except ValueError as e:
                    pass
            
            current_row_no = 1
            curr_set = None
            drawing_list = os.listdir(v['drawing_folder'])
            row_unique_key_no = 0

            for row in ws.rows:
                drawing_found = False
                if start_row < current_row_no:
                    part_no = row[part_no_col_index].value
                    description = row[description_col_index].value
                    qty = row[qty_col_index].value
                    uom = row[uom_col_index].value                            
                    if row[uom_col_index].value == "SET":
                        row_unique_key_no+=1
                        curr_set = part_no
                        cursor.execute("insert into dbo.quotation_component(row, quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                row_unique_key_no, rfq_number, part_no, uom, description, qty, None, 0, None, curr_set)
                        conn.commit()
                    else:
                        drawing_found = False
                        for file in drawing_list:
                            if part_no in file:
                                drawing_found = True
                                #open the file. insert each row into the drawing_parts table     
                                wb2 = load_workbook(v['drawing_folder'] + '/' + file)
                                ws2 = wb2.worksheets[0]
                                row_no = 1
                                
                                row_unique_key_no+=1
                                cursor.execute("insert into dbo.quotation_component(row, quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                row_unique_key_no, rfq_number, part_no, uom, description, qty, None, 1, part_no, curr_set)
                                conn.commit()

                                drawing_part_no_col_index = None
                                drawing_description_col_index = None
                                drawing_qty_col_index = None
                                drawing_uom_col_index = None
                                
                                drawing_columns = []
                                for row in ws2.rows:
                                    if row_no == 1:
                                        for col in row:
                                            drawing_columns.append(str(col.value).lower().strip())
                                
                                drawing_part_no_col_index  = drawing_columns.index(v['drawing_to_db_mapping']['part_no'].lower().strip())
                                drawing_description_col_index = drawing_columns.index(v['drawing_to_db_mapping']['description'].lower().strip())
                                drawing_qty_col_index = drawing_columns.index(v['drawing_to_db_mapping']['qty'].lower().strip())
                                drawing_uom_col_index = drawing_columns.index(v['drawing_to_db_mapping']['uom'].lower().strip())

                                for row in ws2.rows:
                                    if 1 < row_no:
                                        row_unique_key_no+=1
                                        drawing_part_description = row[drawing_description_col_index].value
                                        drawing_part_no = row[drawing_part_no_col_index].value
                                        drawing_part_uom = row[drawing_uom_col_index].value
                                        drawing_part_qty = row[drawing_qty_col_index].value
                                        cursor.execute("insert into dbo.quotation_component(row, quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                row_unique_key_no, rfq_number, drawing_part_no, drawing_part_uom, drawing_part_description, drawing_part_qty, None, 0, part_no, curr_set)
                                        conn.commit()
                                    row_no+=1
                                # shutil.move(v['drawing_folder'] + '/' + file, v['archive_folder'] + '/' + file)
                        if drawing_found == False:
                            row_unique_key_no+=1
                            cursor.execute("insert into dbo.quotation_component(row, quotation_no, component_no, uom, description, quantity, total_price, is_drawing, drawing_no, set_no) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                                row_unique_key_no, rfq_number, part_no, uom, description, qty, None, 0, None, curr_set)
                            conn.commit()            
                current_row_no+=1     
    else:
        print("None of the columns you specified are found")
            #


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

        rfq_list = os.listdir(v['rfq_folder'])
        for each_rfq in rfq_list:
            rfq_location = v['rfq_folder'] + '/' + each_rfq
            to_archive_rfq_location = v['archive_folder'] + '/' + each_rfq
            to_move_unprocessed_rfq_location = v['unprocessed_folder'] + '/' + each_rfq

            rfq_number = Path(rfq_location).stem
            rfq_file_extension = os.path.splitext(rfq_location)[1]
            
            if rfq_file_extension == ".pdf":
                try:
                    processPDF(rfq_location)
                    shutil.move(rfq_location, to_archive_rfq_location)
                except Exception as e:
                    print(e)
                    shutil.move(rfq_location, to_move_unprocessed_rfq_location)
            elif rfq_file_extension == '.xlsx':
                try:
                    processExcel(rfq_location)
                    shutil.move(rfq_location, to_archive_rfq_location)
                except Exception as e:
                    print(e)
                    shutil.move(rfq_location, to_move_unprocessed_rfq_location)
            else:
                shutil.move(rfq_location, to_move_unprocessed_rfq_location)
            
conn.close()
print("Connection closed.")