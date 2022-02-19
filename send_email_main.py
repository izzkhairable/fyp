import send_email as send_email


attachment_list = ['wtf', 'C:/Users/Darren Ho/Documents/GitHub/fyp/sql_connect.cfg']
send_email.sendEmail('darrenho.2019@scis.smu.edu.sg', attachment_list, 'rfq_processed_email_template')