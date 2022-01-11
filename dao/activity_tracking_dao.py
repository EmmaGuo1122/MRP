from model.activity_tracking import ActivityTracking
from utils.db_utilities import db

class ActivityTrackingDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def get_all_activity_tracking(self):
        return ActivityTracking.query.order_by(ActivityTracking.date_of_record.asc()).all()

    def get_activity_tracking_by_id(self, id):
        return ActivityTracking.query.get(int(id))
    
    def get_activity_tracking_by_site(self, site_id):
        return ActivityTracking.query.filter_by(site_id = site_id).order_by(ActivityTracking.date_of_record.asc()).all()
    
    def get_activity_tracking_by_tenant(self, tenant_id):
        return ActivityTracking.query.filter_by(tenant_id = tenant_id).order_by(ActivityTracking.date_of_record.asc()).all()
    
    def get_activity_tracking_by_category(self, activity_category_id):
        return ActivityTracking.query.filter_by(activity_category_id = activity_category_id).order_by(ActivityTracking.date_of_record.asc()).all()
    
    def get_activity_tracking_by_site_and_date_range(self, site_id, from_date, to_date):
        return ActivityTracking.query \
            .filter_by(site_id = site_id) \
            .filter(
                ActivityTracking.date_of_record >= from_date,
                ActivityTracking.date_of_record <= to_date
                ) \
            .order_by(ActivityTracking.date_of_record.asc()).all()

    def save_one_activity_tracking(self, activity_tracking):
        db.session.add(activity_tracking)
    
    def delete_one_activity_tracking(self, activity_tracking):
        db.session.delete(activity_tracking)