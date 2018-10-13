from HELPERS.HELPER_Login_Info import *
import smtplib

# This is a SMS Notification Class
class SMS:
    def __init__(self):
        pass

    def DeleteResources(self):
        # Send a text message
        subject = "Resource Group: " + GROUP_NAME + " has been deleted"
        email_body = "Resource Group: " + GROUP_NAME + " has been deleted"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(EMAIL_SENDER,
                   EMAIL_PASSWORD,
                   )
        conn.sendmail(EMAIL_SENDER,
                      RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def CreateVM(self,Instance):
        # Send a text message
        subject = "Virtual Machine: " + str(Instance) + " has been created"
        email_body = "Virtual Machine: " + str(Instance) + " has been created"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(EMAIL_SENDER,
                   EMAIL_PASSWORD,
                   )
        conn.sendmail(EMAIL_SENDER,
                      RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def FoundIP(self,Instance):
        # Send a text message
        subject = "IP for Virtual Machine: " + str(Instance) + " has been found"
        email_body = "IP for Virtual Machine: " + str(Instance) + " has been found"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(EMAIL_SENDER,
                   EMAIL_PASSWORD,
                   )
        conn.sendmail(EMAIL_SENDER,
                      RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()
