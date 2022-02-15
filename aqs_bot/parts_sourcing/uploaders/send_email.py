import win32com.client as win32


def send_email(component_no, description, unit_price):
    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)
    mail.To = "izzkhair@gmail.com"
    mail.Subject = "Item pricing needed to be added to item master"
    # mail.Body = "Message body"
    mail.HTMLBody = f"<h2>Please add the folowing item to Item Master</h2><p>Component Number:{component_no}</p><p>Description:{description}</p><p>Unit Price:{unit_price}</p>"

    mail.Send()
