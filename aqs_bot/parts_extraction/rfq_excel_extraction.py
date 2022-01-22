import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font
import os

with open('aqs_bot/parts_extraction/config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for key, v in data.items():
        selected_column_list = v['bom_column'].split(',')
        selected_column_list = [selected_column.lower().strip() for selected_column in selected_column_list] 
        wb = load_workbook('aqs_bot/parts_extraction/input/26VSMTC-0012-ST=15.xlsx')
        ws = wb['26VSMTC-0012-ST=14']
        start_row = 0
        selected_columns_index_list = []
        confirmed_columns_list = []

        row_col_index = None
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
                if str(col.value).lower().strip() == v['db_col_mapping']['row'].lower():
                    row_col_index = current_col_no                
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
            if start_row < current_row_no:

                row_no = row[row_col_index].value
                part_no = row[part_no_col_index].value
                description = row[description_col_index].value
                qty = row[qty_col_index].value
                uom = row[uom_col_index].value
                price = row[price_col_index].value

                if row[uom_col_index].value == "SET":
                    curr_set = part_no
                    print(curr_set)
                else:
                    print(part_no)
                    for file in drawing_list:
                        if part_no in file:
                            pass
                            #open the file. insert each row into the drawing_parts table
                    
            current_row_no+=1     
