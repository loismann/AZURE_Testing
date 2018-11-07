
import smtplib

# This is a SMS Notification Class
class SMS:
    def __init__(self):
        pass

    def DeleteResources(self,Login_Class):
        # Send a text message
        subject = "Resource Group: " + Login_Class.GROUP_NAME + " has been deleted"
        email_body = "Resource Group: " + Login_Class.GROUP_NAME + " has been deleted"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def CreateVM(self,Instance,Login_Class):
        # Send a text message
        subject = "Virtual Machine: " + str(Instance) + " has been created"
        email_body = "Virtual Machine: " + str(Instance) + " has been created"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def FoundIP(self,Instance,Login_Class):
        # Send a text message
        subject = "IP for Virtual Machine: " + str(Instance) + " has been found"
        email_body = "IP for Virtual Machine: " + str(Instance) + " has been found"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def DGPfilesCopiedToCloud(self,Instance,Login_Class):
        # Send a text message
        subject = "DGP Resource Files for VM: " + str(Instance) + " have been copied to Azure"
        email_body = "DGP Resource Files for VM: " + str(Instance) + " have been copied to Azure"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def SimulationsStarted(self,Instance,Login_Class):
        # Send a text message
        subject = "Simulations launched on VM: " + str(Instance)
        email_body = "Simulations launched on VM: " + str(Instance)
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def SimulationsComplete(self,Login_Class):
        # Send a text message
        subject = "Simulations Complete!"
        email_body = "Simulations Complete!"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()

    def HDRsCopied(self,Login_Class):
        # Send a text message
        subject = "HDR Files Copied Back To Local Machine"
        email_body = "HDR Files Copied Back To Local Machine"
        conn = smtplib.SMTP('smtp.gmail.com', 587)
        conn.ehlo()
        conn.starttls()
        conn.login(Login_Class.EMAIL_SENDER,
                   Login_Class.EMAIL_PASSWORD,
                   )
        conn.sendmail(Login_Class.EMAIL_SENDER,
                      Login_Class.RECIPIENT,
                      'Subject:' + subject + '\n' + email_body
                      )
        conn.quit()