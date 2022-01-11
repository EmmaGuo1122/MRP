from model.system_configuration import SystemConfiguration
from utils.db_utilities import db
from sqlalchemy import select

class SystemConfigurationDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_configuration_by_id(self, id):
        return SystemConfiguration.query.get(int(id))
    
    def get_configuration_by_key(self, conf_key):
        return SystemConfiguration.query.filter_by(conf_key = conf_key).first()
    
    def get_all_configurations(self):
        return SystemConfiguration.query.order_by(SystemConfiguration.conf_key.asc()).all()

    def save_one_configuration(self, system_configruation):
        db.session.add(system_configruation)
    
    def delete_one_configuration(self, conf):
        db.session.delete(conf)