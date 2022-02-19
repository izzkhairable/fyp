import win32com.client
import configparser
import yaml
config = configparser.ConfigParser()
config.read('send_email.cfg')
outlook = win32com.client.Dispatch('outlook.application')

def sendEmail(recipient, attachment_list, template_type):
    with open('send_email.yaml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

        mail = outlook.CreateItem(0)
        
        mail.To = recipient
        mail.Subject = data[template_type]['subject']
        # mail.HTMLBody = '<h3>This is HTML Body</h3>'
        mail.Body = data[template_type]['body']
        if attachment_list != None:
            for attachment in attachment_list:
                try:
                    mail.Attachments.Add(attachment)
                except:
                    pass
        mail.Send()


