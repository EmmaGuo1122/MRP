from datetime import datetime
from dao.activity_tracking_dao import ActivityTrackingDAO
from service.email_service import EmailService
from service.site_service import SiteService
from service.system_configuration_service import SystemConfigurationService
from utils.db_utilities import db
from utils import prj_constants, string_utilities
from datetime import datetime, timedelta
from flask_login import current_user

class ActivityTrackingService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_all_activity_tracking(self):
        with ActivityTrackingDAO() as dao:
            return dao.get_all_activity_tracking()
    
    def get_activity_tracking_by_id(self, id):
        with ActivityTrackingDAO() as dao:
            return dao.get_activity_tracking_by_id(id)
        
    def get_activity_tracking_by_site(self, site_id):
        with ActivityTrackingDAO() as dao:
            return dao.get_activity_tracking_by_site(site_id)

    def get_activity_tracking_by_site_and_date_range(self, site_id, from_date, to_date):
        with ActivityTrackingDAO() as dao:
            return dao.get_activity_tracking_by_site_and_date_range(site_id, from_date, to_date)
        
    def get_activity_tracking_by_tenant(self, tenant_id):
        with ActivityTrackingDAO() as dao:
            return dao.get_activity_tracking_by_tenant(tenant_id)
    
    def get_activity_tracking_by_category(self, activity_category_id):
        with ActivityTrackingDAO() as dao:
            return dao.get_activity_tracking_by_category(activity_category_id)
    
    def save_one_activity_tracking(self, activity_tracking):
        with ActivityTrackingDAO() as dao:
            activity_tracking.updated_by = current_user.id
            activity_tracking.updated_on = datetime.now().isoformat()
            dao.save_one_activity_tracking(activity_tracking)
            db.session.commit()

    def save_many_activity_tracking(self, activity_tracking_list):
        with ActivityTrackingDAO() as dao:
            for r in activity_tracking_list:
                dao.save_one_activity_tracking(r)
            db.session.commit()
    
    def delete_one_activity_tracking(self, activity_tracking_id):
        with ActivityTrackingDAO() as dao:
            activity_tracking = dao.get_activity_tracking_by_id(activity_tracking_id)
            dao.delete_one_activity_tracking(activity_tracking)
            db.session.commit()

def tenant_scoring_job():
    from flask import current_app
    with current_app.app_context():
        site_service = SiteService()
        system_configuration_service = SystemConfigurationService()
        activity_tracking_service = ActivityTrackingService()

        low_score = system_configuration_service.get_configuration_by_key(prj_constants.CONF_KEY_SCORE_ALERT_LEVEL_LOW)
        medium_score = system_configuration_service.get_configuration_by_key(prj_constants.CONF_KEY_SCORE_ALERT_LEVEL_MEDIUM)
        high_score = system_configuration_service.get_configuration_by_key(prj_constants.CONF_KEY_SCORE_ALERT_LEVEL_HIGH)
        threshold = system_configuration_service.get_configuration_by_key(prj_constants.CONF_KEY_SCORE_ALERT_THRESHOLD)
        tracking_window_in_days = system_configuration_service.get_configuration_by_key(prj_constants.CONF_KEY_ACTIVITY_TRACKING_WINDOW)

        low_score = int(low_score.conf_value) if low_score and low_score.conf_value else prj_constants.DEFAULT_SCORE_ALERT_LEVEL_LOW
        medium_score = int(medium_score.conf_value) if medium_score and medium_score.conf_value else prj_constants.DEFAULT_SCORE_ALERT_LEVEL_MEDIUM
        high_score = int(high_score.conf_value) if high_score and high_score.conf_value else prj_constants.DEFAULT_SCORE_ALERT_LEVEL_HIGH
        threshold = int(threshold.conf_value) if threshold and threshold.conf_value else prj_constants.DEFAULT_SCORE_ALERT_THRESHOLD
        tracking_window_in_days = int(tracking_window_in_days.conf_value) \
            if tracking_window_in_days and tracking_window_in_days.conf_value \
            else prj_constants.DEFAULT_ACTIVITY_TRACKING_WINDOW

        to_date = string_utilities.convert_yyyymmdd_str_to_int(
            (datetime.today() - timedelta(days=1)).strftime('%Y/%m/%d')
        )
        from_date = string_utilities.convert_yyyymmdd_str_to_int(
            (datetime.today() - timedelta(days=tracking_window_in_days)).strftime('%Y/%m/%d')
        )

        for s in site_service.get_all_sites():
            tmp_map = {}
            tracking_records = activity_tracking_service.get_activity_tracking_by_site_and_date_range(s.id, from_date, to_date)
            for r in tracking_records:
                score = low_score if r.activity_category.alert_level == prj_constants.ALERT_LEVEL_LOW \
                    else medium_score if r.activity_category.alert_level == prj_constants.ALERT_LEVEL_MEDIUM \
                    else high_score
                    
                new_score = score + (tmp_map.get(r.tenant.unique_name) if r.tenant.unique_name in tmp_map else 0)
                tmp_map.update({r.tenant.unique_name: new_score})

            over_threshold_list = [{k: v} for k, v in tmp_map.items() if v >= threshold]
            if over_threshold_list and len(over_threshold_list) > 0:
                EmailService().send_tracking_result_email(s, over_threshold_list, from_date, to_date)




    
