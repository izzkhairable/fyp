import yaml
from openpyxl import Workbook, load_workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.styles import Font

with open('aqs_bot/parts_extraction/config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    for key, v in data.items():
        column_list = v['bom_column'].split(',')
        wb = load_workbook('aqs_bot/parts_extraction/input/26VSMTC-0012-ST=15.xlsx')
        ws = wb['26VSMTC-0012-ST=14']
        start_row = 0
        selected_columns_index_list = []
        confirmed_columns_list = []
        for row in ws.rows:
            for col in row:
                print(col.value)