from dao.site_dao import SiteDAO
from model.notification_email import NotificationEmail
from utils.db_utilities import db
from flask_login import current_user
import datetime

class SiteService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_all_sites(self):
        with SiteDAO() as dao:
            return dao.get_all_sites()
    
    def get_site_by_id(self, id):
        with SiteDAO() as dao:
            return dao.get_site_by_id(id)
    
    def get_site_by_name(self, name):
        with SiteDAO() as dao:
            return dao.get_site_by_name(name)
    
    def get_site_by_manager(self, manager_id):
        with SiteDAO() as dao:
            return dao.get_site_by_manager(manager_id)
    
    def save_one_site(self, site, notification_emails):
        with SiteDAO() as dao:
            site.updated_by = current_user.id
            site.updated_on = datetime.datetime.now().isoformat()
            dao.save_one_site(site)
            db.session.commit()
            persisted_site = None
            if not site.id:
                persisted_site = dao.get_latest_site()
            else:
                persisted_site = dao.get_site_by_id(site.id)
            
            for e in dao.get_notification_email_by_site(persisted_site.id):
                if e.notification_email not in notification_emails:
                    dao.delete_notification_email(e)

            for e in notification_emails:
                if not dao.get_notification_email(persisted_site.id, e):
                    dao.save_one_notification_email(NotificationEmail(None, persisted_site.id, e))
            
            db.session.commit()
    
    def delete_one_site(self, site_id):
        with SiteDAO() as dao:
            for e in dao.get_notification_email_by_site(site_id):
                dao.delete_notification_email(e)

            site = dao.get_site_by_id(site_id)
            dao.delete_one_site(site)
            db.session.commit()