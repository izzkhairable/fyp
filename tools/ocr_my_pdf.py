import os

import requests
import pdfplumber

def download_file(url):
    local_filename = url.split('/')[-1]
    
    with requests.get(url) as r:
        assert r.status_code == 200, f'error, status code is {r.status_code}'
        with open(local_filename, 'wb') as f:
            f.write(r.content)
        
    return local_filename

# invoice = 'https://bit.ly/2UJgUpO'
# invoice_pdf = download_file(invoice)



#os.system(f'ocrmypdf "C:/Users/Darren Ho/Documents/GitHub/fyp/aqs_bot/win_loss_tracker/po/MakinoSampleDO.pdf" "C:/Users/Darren Ho/Documents/GitHub/fyp/aqs_bot/win_loss_tracker/po/output.pdf"')

rfq_number = '28VSMTC-0003-ST.6'.split('-')
rfq = "-".join(rfq_number[0:len(rfq_number)-1])



with pdfplumber.open('C:/Users/Darren Ho/Documents/GitHub/fyp/aqs_bot/win_loss_tracker/po/output.pdf') as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    #print(text)


print(rfq in text)