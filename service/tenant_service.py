from dao.tenant_dao import TenantDAO
from utils.db_utilities import db
from flask_login import current_user
import datetime

class TenantService:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        #if db.session.is_active:
        #    db.session.close()
        pass

    def get_all_tenants(self):
        with TenantDAO() as dao:
            return dao.get_all_tenants()
    
    def get_tenant_by_id(self, id):
        with TenantDAO() as dao:
            return dao.get_tenant_by_id(id)
        
    def get_tenant_by_unique_name(self, unique_name, site_id):
        with TenantDAO() as dao:
            return dao.get_tenant_by_unique_name(unique_name, site_id)

    def get_tenant_by_site(self, site_id):
        with TenantDAO() as dao:
            return dao.get_tenant_by_site(site_id)
    
    def save_one_tenant(self, tenant):
        with TenantDAO() as dao:
            tenant.updated_by = current_user.id
            tenant.updated_on = datetime.datetime.now().isoformat()
            dao.save_one_tenant(tenant)
            db.session.commit()
    
    def delete_one_tenant(self, tenant_id):
        with TenantDAO() as dao:
            tenant = dao.get_tenant_by_id(tenant_id)
            dao.delete_one_tenant(tenant)
            db.session.commit()