from model.tenant import Tenant
from utils.db_utilities import db
from sqlalchemy import select

class TenantDAO:

    def __init__(self):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def get_tenant_by_id(self, id):
        return Tenant.query.get(int(id))
    
    def get_tenant_by_unique_name(self, unique_name, site_id):
        return Tenant.query.filter_by(unique_name = unique_name, site_id = site_id).first()
    
    def get_tenant_by_site(self, site_id):
        return Tenant.query.filter_by(site_id = site_id).order_by(Tenant.unit.asc(), Tenant.status.asc()).all()
    
    def get_all_tenants(self):
        return Tenant.query.order_by(Tenant.site_id.asc(), Tenant.unit.asc(), Tenant.status.asc()).all()

    def save_one_tenant(self, tenant):
        db.session.add(tenant)
    
    def delete_one_tenant(self, tenant):
        db.session.delete(tenant)