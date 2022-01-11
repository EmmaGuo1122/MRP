from model.site import Site
from model.notification_email import NotificationEmail
from utils.db_utilities import db
from sqlalchemy import select

class SiteDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_site_by_id(self, id):
        return Site.query.get(int(id))
    
    def get_all_sites(self):
        return Site.query.order_by(Site.name.asc()).all()
    
    def get_site_by_manager(self, manager_id):
        return Site.query.filter_by(manager_id = manager_id).order_by(Site.name.asc()).all()
    
    def get_latest_site(self):
        return Site.query.order_by(Site.id.desc()).first()
    
    def get_site_by_name(self, name):
        return Site.query.filter_by(name = name).first()

    def save_one_site(self, site):
        db.session.add(site)
    
    def delete_one_site(self, site):
        db.session.delete(site)
    
    def get_notification_email(self, site_id, notification_email):
        return NotificationEmail.query.filter_by(site_id = site_id).filter_by(notification_email = notification_email).first()
    
    def get_notification_email_by_site(self, site_id):
        return NotificationEmail.query.filter_by(site_id = site_id).all()
    
    def delete_notification_email(self, notification_email):
        db.session.delete(notification_email)
    
    def save_one_notification_email(self, notification_email):
        db.session.add(notification_email)
