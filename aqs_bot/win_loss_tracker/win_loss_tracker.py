import os
import yaml
import requests
import pdfplumber
import pyodbc
import datetime


conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-KMU57HS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()

# quotation_list = cursor.execute("select * from dbo.quotation where status<>?", 'haha')
quotation_list = cursor.execute("select quotation_no, rfq_date from dbo.quotation where status=?", 'sent')
result = quotation_list.fetchall()

with open('aqs_bot/win_loss_tracker/config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)
    po_folder = data['po_folder']
    loss_after_x_days = data['loss_after_x_days']

    text_list = []

    po_list = os.listdir(po_folder)
    for po in po_list:
        with pdfplumber.open(po_folder + '\\' + po) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
        if len(text) == 0:
            print("Performing OCR.")
            os.system(f'ocrmypdf "' + po_folder + '\\' + po + '" "' + po_folder + '\\temp.pdf' + '"')
            with pdfplumber.open(po_folder + '\\temp.pdf') as pdf:
                page = pdf.pages[0]
                text = page.extract_text()
            os.remove(po_folder + '\\temp.pdf')
        text_list.append(text)

    for quotation in result:
        rfq_split = quotation.quotation_no.split('-')
        rfq_no_without_rev = "-".join(rfq_split[0:len(rfq_split)-1])

        no_of_days_since_rfq_received = (datetime.datetime.today() - quotation.rfq_date).days

    #https://ocrmypdf.readthedocs.io/en/latest/installation.html#installing-on-windows
        for each_text in text_list:
            if rfq_no_without_rev in each_text:
                print("Win: " + quotation.quotation_no)
                cursor.execute("update dbo.quotation set status=? where quotation_no=?", 'win', quotation.quotation_no)
                conn.commit()
                break

            elif no_of_days_since_rfq_received > loss_after_x_days:
                print("Lose: " + quotation.quotation_no)
                cursor.execute("update dbo.quotation set status=? where quotation_no=?", 'lose', quotation.quotation_no)
                conn.commit()        
                    
conn.close()

'''
CHANGES TO MAKE
1. SCAN ALL RFQS. STORE IT INTO ARRAY

THEN READ EACH PO ONLY ONCE, CHECK IF ANY OF THE TEXT IN ARRAY IS IN PO
'''