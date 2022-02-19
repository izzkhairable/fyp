import os
import yaml
import requests
import pdfplumber
import pyodbc
import datetime
import configparser

config = configparser.ConfigParser()
config.read('sql_connect.cfg')
config2 = configparser.ConfigParser()#
config2.read('aqs_bot\win_loss_tracker\win_loss_tracker.cfg')

conn = pyodbc.connect('Driver=' + config['database']['driver'] + ';'
                      'Server=' + config['database']['server'] + ';'
                      'Database=' + config['database']['database'] + ';'
                      'Trusted_Connection=' + config['database']['trusted_connection'] + ';')
cursor = conn.cursor()

# quotation_list = cursor.execute("select * from dbo.quotation where status<>?", 'haha')
quotation_list = cursor.execute("select quotation_no, rfq_date from dbo.quotation where status=? or status=?", 'sent', 'lose')
result = quotation_list.fetchall()

po_folder = config2['win_loss_tracker']['po_folder']
loss_after_x_days = int(config2['win_loss_tracker']['loss_after_x_days'])

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
