from service.system_configuration_service import SystemConfigurationService
from model.system_configuration import SystemConfiguration
from utils import prj_constants, string_utilities
from utils.db_utilities import db
import smtplib, ssl

class EmailService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def send_email_to_new_user(self, user_obj, tmp_password):
        content = "Hello " + user_obj.get_displayed_name+",\n\n"
        content += "Welcome to Tenant Tracking Tool! Below is your username and password:\n"
        content += "\t Username: "+user_obj.username+"\n"
        content += "\t Password: "+tmp_password+"\n\n"
        content += "Best regards,"

        subject = "[Tenant Tracking Tool] Information to log in"

        self.send_email(subject, content, user_obj.email)
    
    def send_tracking_result_email(self, site, over_threshold_records, from_date, to_date):
        #subject = "[Tenant Tracking Tool] Notification of tenants who may go off track"
        subject = "[Tenant Tracking Tool] Site "
        subject += site.name
        subject += " - Notification of tenants who may go off track"

        from_date_str = string_utilities.convert_int_to_yyyymmdd_str(from_date)
        to_date_str = string_utilities.convert_int_to_yyyymmdd_str(to_date)
        content = "Hello, \n\n"
        content += "Tracking records of the site "+site.name+" from "+from_date_str+"-"+to_date_str+" indicate that the below tenants may go off track:\n"
        for t in over_threshold_records:
            content += "\t " + list(t.keys())[0]
        content += "\n\nBest regards,"

        site_mngr_email = None
        if site.manager and site.manager.email:
            site_mngr_email = site.manager.email
            self.send_email(subject, content, site.manager.email)
        
        if site.notification_emails:
            for e in site.notification_emails:
                if e.notification_email != site_mngr_email:
                    self.send_email(subject, content, e.notification_email)
    
    def build_message_text(self, subject, content, receiver):
        message = ""
        message += "Subject: "+subject
        message += "\n"
        message += "To: "+receiver
        message += "\n"
        message += content

        return message


    def send_email(self, subject, content, receiver_address):
        conf_service = SystemConfigurationService()

        conf = conf_service.get_configuration_by_key(prj_constants.CONF_KEY_SENDER_EMAIL_ADDRESS)
        sender_address = conf.conf_value if conf else None

        conf = conf_service.get_configuration_by_key(prj_constants.CONF_KEY_SENDER_EMAIL_PASSWORD)
        sender_password = conf.conf_value if conf else None

        conf = conf_service.get_configuration_by_key(prj_constants.CONF_KEY_SSL_PORT)
        ssl_port = int(conf.conf_value) if conf else None

        conf = conf_service.get_configuration_by_key(prj_constants.CONF_KEY_SMTP_SERVER)
        smtp_server = conf.conf_value if conf else None

        if sender_address and sender_password and ssl_port and smtp_server:
            message = self.build_message_text(subject, content, receiver_address)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, ssl_port, context=context) as server:
                server.login(sender_address, sender_password)
                server.sendmail(sender_address, receiver_address, message)


