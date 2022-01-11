from dao.system_configuration_dao import SystemConfigurationDAO
from utils.db_utilities import db
from flask_login import current_user
import datetime

class SystemConfigurationService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_all_configurations(self):
        with SystemConfigurationDAO() as dao:
            return dao.get_all_configurations()
    
    def get_configuration_by_key(self, conf_key):
        with SystemConfigurationDAO() as dao:
            return dao.get_configuration_by_key(conf_key)

    def get_configuration_by_id(self, id):
        with SystemConfigurationDAO() as dao:
            return dao.get_configuration_by_id(id)
    
    def save_one_configuration(self, configuration):
        with SystemConfigurationDAO() as dao:
            configuration.updated_by = current_user.id
            configuration.updated_on = datetime.datetime.now().isoformat()
            dao.save_one_configuration(configuration)
            db.session.commit()
    
    def delete_one_configuration(self, conf_id):
        with SystemConfigurationDAO() as dao:
            conf_obj = self.get_configuration_by_id(conf_id)
            dao.delete_one_configuration(conf_obj)
            db.session.commit()