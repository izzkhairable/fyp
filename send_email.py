import win32com.client
outlook = win32com.client.Dispatch('outlook.application')

mail = outlook.CreateItem(0)

mail.To = 'darrenho.2019@scis.smu.edu.sg'
mail.Subject = 'Sample Email'
mail.HTMLBody = '<h3>This is HTML Body</h3>'
mail.Body = "This is the normal body"
mail.Attachments.Add(r'C:\Users\Darren Ho\Documents\GitHub\fyp\aqs.sql')
mail.Send()