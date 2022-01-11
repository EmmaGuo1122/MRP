from flask import Flask, jsonify, request, render_template, redirect, session
from flask_login import fresh_login_required, login_required, current_user, login_user, logout_user
from flask_login import LoginManager
from model.site import Site
from model.tenant import Tenant
from model.activity_category import ActivityCategory
from model.activity_tracking import ActivityTracking
from model.api_response import APIResponse
from model.user import User
from service.email_service import EmailService
from service.user_service import UserService
from service.site_service import SiteService
from service.tenant_service import TenantService
from service.system_configuration_service import SystemConfigurationService
from service.activity_category_service import ActivityCategoryService
from service.activity_tracking_service import ActivityTrackingService, tenant_scoring_job
from utils.db_utilities import db
from utils import string_utilities
from utils import prj_constants
from datetime import timedelta, datetime
from flask_apscheduler import APScheduler
import json
import pandas as pd
import atexit

class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "tenant_scoring_job",
            "func": "service.activity_tracking_service:tenant_scoring_job",
            "args": (),
            "trigger": "interval",
            "hours": 24
        }
    ]

    SCHEDULER_API_ENABLED = True

def create_app():
    app = Flask(__name__, template_folder='Templates')
    app.secret_key = 'xyz'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tenant_tracking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.config.from_object(Config())

    # uncomment the below lines when you deploy the app on a non-free hosting server - START
    # scheduler = APScheduler()
    # scheduler.init_app(app)
    # scheduler.start()

    # atexit.register(lambda: scheduler.shutdown())
    # uncomment the below lines when you deploy the app on a non-free hosting server - END

    login = LoginManager()
    login.init_app(app)
    login.login_view = 'login'
    login.session_protection = "strong"

    @login.user_loader
    def load_user(id):
        with UserService() as service:
            return service.get_user_by_id(int(id))

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)

    @app.route('/')
    @login_required
    def index():
        # build final data
        data = {
            'current_user': current_user.serialize()
        }
        message = session.pop('message') if 'message' in session else None
        if message:
            data['message'] = message

        return render_template('index.html', data=data)

    @app.route('/users')
    @login_required
    def user_management():
        # get user list
        user_list = []
        user_service = UserService()
        site_service = SiteService()

        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            user_list = user_service.get_all_users()
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            user_list.append(user_service.get_user_by_id(current_user.id))
            site_list = site_service.get_site_by_manager(current_user.id)
            for site in site_list:
                user_list.extend(user_service.get_users_by_site(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            user_list = [user_service.get_user_by_id(current_user.id)]

        # get user status list
        user_status_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN, prj_constants.USER_ROLE_SITE_MANAGER]:
            user_status_list = [prj_constants.USER_STATUS_ACTIVE, prj_constants.USER_STATUS_LOCKED]

        # get user role list
        user_role_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            user_role_list = [prj_constants.USER_ROLE_ADMIN, prj_constants.USER_ROLE_SITE_MANAGER, prj_constants.USER_ROLE_USER]
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            user_role_list = [prj_constants.USER_ROLE_SITE_MANAGER, prj_constants.USER_ROLE_USER]

        # get site list
        site_list = []    
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            site_list = site_service.get_all_sites()
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            site_list = site_service.get_site_by_manager(current_user.id)

        # build final data
        data = {
            'current_user': current_user.serialize(),
            'user_list': [u.serialize() for u in user_list],
            'user_status_list': user_status_list,
            'user_role_list': user_role_list,
            'site_list': [s.serialize() for s in site_list]
        }

        return render_template('users.html', data=data)

    @app.route('/sites')
    @login_required
    def site_management():
        # get site list
        site_list = []
        user_service = UserService()
        site_service = SiteService()

        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            site_list = site_service.get_all_sites()
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                site_list.append(site_service.get_site_by_id(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                site_list.append(site_service.get_site_by_id(site.id))

        # get province list
        province_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN, prj_constants.USER_ROLE_SITE_MANAGER]:
            province_list.extend(prj_constants.CANADA_PROVINCE_LIST)

        # get manager list
        manager_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN, prj_constants.USER_ROLE_SITE_MANAGER]:
            manager_list.extend(user_service.get_users_by_role(prj_constants.USER_ROLE_SITE_MANAGER))


        # build final data
        data = {
            'current_user': current_user.serialize(),
            'site_list': [s.serialize() for s in site_list],
            'province_list': province_list,
            'manager_list': [u.serialize() for u in manager_list],
        }

        return render_template('sites.html', data=data)

    @app.route('/tenants')
    @login_required
    def tenant_management():
        # get site list
        site_list = []
        tenant_service = TenantService()
        site_service = SiteService()

        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            site_list = site_service.get_all_sites()
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                site_list.append(site_service.get_site_by_id(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                site_list.append(site_service.get_site_by_id(site.id))

        # get tenant list
        tenant_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            tenant_list.extend(tenant_service.get_all_tenants())
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                tenant_list.extend(tenant_service.get_tenant_by_site(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                tenant_list.extend(tenant_service.get_tenant_by_site(site.id))

        # get tenant status list
        status_list = [prj_constants.TENANT_STATUS_ACTIVE, prj_constants.TENANT_STATUS_MOVED_OUT]          

        # build final data
        data = {
            'current_user': current_user.serialize(),
            'site_list': [s.serialize() for s in site_list],
            'tenant_list': [t.serialize() for t in tenant_list],
            'status_list': status_list
        }

        return render_template('tenants.html', data=data)

    @app.route('/activity_categories')
    @login_required
    def activity_category_management():
        activity_category_service = ActivityCategoryService()
        activity_category_list = activity_category_service.get_all_activity_categories()

        alert_level_list = [
            prj_constants.ALERT_LEVEL_LOW,
            prj_constants.ALERT_LEVEL_MEDIUM,
            prj_constants.ALERT_LEVEL_HIGH
        ]         

        # build final data
        data = {
            'current_user': current_user.serialize(),
            'activity_category_list': [c.serialize() for c in activity_category_list],
            'alert_level_list': alert_level_list
        }

        return render_template('activity_categories.html', data=data)

    @app.route('/tracking')
    @login_required
    def tracking_management():
        activity_tracking_service = ActivityTrackingService()
        activity_category_service = ActivityCategoryService()
        site_service = SiteService()
        tenant_service = TenantService()

        # get site list
        site_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            site_list.extend(site_service.get_all_sites())
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                site_list.append(site_service.get_site_by_id(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                site_list.append(site_service.get_site_by_id(site.id))

        # get tenant list
        tenant_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            tenant_list.extend(tenant_service.get_all_tenants())
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                tenant_list.extend(tenant_service.get_tenant_by_site(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                tenant_list.extend(tenant_service.get_tenant_by_site(site.id))

        # get activity category list
        activity_category_list = activity_category_service.get_all_activity_categories()

        # get activity tracking list
        activity_tracking_list = []
        if current_user.role in [prj_constants.USER_ROLE_SUPER_ADMIN, prj_constants.USER_ROLE_ADMIN]:
            activity_tracking_list.extend(activity_tracking_service.get_all_activity_tracking())
        elif current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
            sites = site_service.get_site_by_manager(current_user.id)
            for site in sites:
                activity_tracking_list.extend(activity_tracking_service.get_activity_tracking_by_site(site.id))
        elif current_user.role == prj_constants.USER_ROLE_USER:
            site = site_service.get_site_by_id(current_user.site_id)
            if site:
                activity_tracking_list.extend(activity_tracking_service.get_activity_tracking_by_site(site.id))   

        # build final data
        data = {
            'current_user': current_user.serialize(),
            'activity_tracking_list': [t.serialize() for t in activity_tracking_list],
            'activity_category_list': [c.serialize() for c in activity_category_list],
            'tenant_list': [t.serialize() for t in tenant_list],
            'site_list': [s.serialize() for s in site_list],
        }

        return render_template('tracking.html', data=data)

    @app.route('/system_configurations')
    @login_required
    def configuration_management():
        if not current_user.can_access_system_configuration():
            message = 'Sorry! You do not have permission to access this feature!'
            session['message'] = message
            return redirect('/')

        # get site list
        system_configuration_service = SystemConfigurationService()
        system_configuration_list = system_configuration_service.get_all_configurations()            

        # build final data
        data = {
            'current_user': current_user.serialize(),
            'system_configuration_list': [c.serialize() for c in system_configuration_list],
        }

        return render_template('system_configurations.html', data=data)

    @app.route('/login', methods = ['POST', 'GET'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')

        data = {'is_error': False, 'error_message': ''}     
        if request.method == 'POST':
            username = request.form['username']

            if not username:
                data['is_error'] = True
                data['error_message'] = 'Username cannot be empty'
                return render_template('login.html', data=data)

            password = request.form['password']
            if not password:
                data['is_error'] = True
                data['error_message'] = 'Password cannot be empty'
                return render_template('login.html', data=data)

            with UserService() as service:
                user = service.get_user_by_username(username)
                if user is not None and user.check_password(password):
                    login_user(user,remember=False, duration=timedelta(microseconds=0), force=False, fresh=True)
                    return redirect('/')
                else:
                    data['is_error'] = True
                    data['error_message'] = 'Username and password do not match'
                    return render_template('login.html', data=data)

        return render_template('login.html', data=data)

    @app.route("/logout", methods = ['POST', 'GET'])
    @login_required
    def logout():
        logout_user()
        return redirect("/login")

    @app.route("/change_password", methods = ['GET'])
    @login_required
    def to_change_password_page():
        data = {'is_error': False, 'error_message': ''}
        return render_template('change_password.html', data=data)

    @app.route("/change_password", methods = ['POST'])
    @login_required
    def change_password():
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        data = {'is_error': False, 'error_message': ''}
        if not current_password:
            data['is_error'] = True
            data['error_message'] = 'Current password cannot be empty.'
            return render_template('change_password.html', data=data)

        if not new_password:
            data['is_error'] = True
            data['error_message'] = 'New password cannot be empty.'
            return render_template('change_password.html', data=data)

        if not confirm_new_password:
            data['is_error'] = True
            data['error_message'] = 'Confirm new password cannot be empty.'
            return render_template('change_password.html', data=data)

        if new_password != confirm_new_password:
            data['is_error'] = True
            data['error_message'] = 'New password and Confirm new password do not match'
            return render_template('change_password.html', data=data)

        if not current_user.check_password(current_password):
            data['is_error'] = True
            data['error_message'] = 'Current password is not correct'
            return render_template('change_password.html', data=data)

        if not string_utilities.validate_password(new_password):
            data['is_error'] = True
            data['error_message'] = '''
            Password must be mininum 8 in length, and contains 
            - at least a lower character
            - and at least an upper character
            - and at least one digit
            - and at least one special character @$!%*?&\/
            '''
            return render_template('change_password.html', data=data)

        with UserService() as service:
            u = service.get_user_by_id(current_user.id)
            u.set_password(new_password)
            service.save_one_user(u)
            data['success_message'] = 'Your message has been changed successfully!'

            return render_template("login.html", data=data)

    # APIs
    @app.route('/api/trigger_job', methods = ['GET'])
    @login_required
    def trigger_job():
        tenant_scoring_job()
        return APIResponse(is_successful=True, error_message='', data={}).serialize()


    @app.route('/api/user/delete', methods = ['DELETE'])
    @login_required
    def delete_user():
        user_id = int(request.get_data())

        with UserService() as service:
            resp = service.delete_user(user_id)
            return APIResponse(is_successful=resp['is_successfull'], error_message=resp['error_message'], data={}).serialize()

    @app.route('/api/user/<_id>', methods = ['GET'])
    @login_required
    def get_user(_id):
        user_id = int(_id)

        with UserService() as service:
            u = service.get_user_by_id(user_id)
            return u.serialize()

    @app.route('/api/user/save', methods = ['POST'])
    @login_required
    def save_user():
        user_dict = json.loads(request.get_data())

        user_id = int(user_dict['id']) if 'id' in user_dict and user_dict['id'] else None
        first_name = user_dict['first_name'] if 'first_name' in user_dict else None
        last_name = user_dict['last_name'] if 'last_name' in user_dict else None
        username = user_dict['username'] if 'username' in user_dict else None
        role = user_dict['role'] if 'role' in user_dict else None
        status = user_dict['status'] if 'status' in user_dict else None
        email = user_dict['email'] if 'email' in user_dict else None
        site_id = int(user_dict['site_id']) if user_dict['site_id'] and role == prj_constants.USER_ROLE_USER else None

        if not username:
            return APIResponse(is_successful=False, error_message='Username cannot be empty.', data={}).serialize()

        if not string_utilities.validate_username(username):
            return APIResponse(is_successful=False, error_message='Username must be 5-20 characters in length, and consists of alphanumeric characters and/or ._- only.', data={}).serialize()

        if not email:
            return APIResponse(is_successful=False, error_message='Email cannot be empty.', data={}).serialize()

        if not string_utilities.validate_email(email):
            return APIResponse(is_successful=False, error_message='Email does not match a valid format.', data={}).serialize()

        if role == prj_constants.USER_ROLE_USER and not site_id:
            return APIResponse(is_successful=False, error_message='Site must be specified.', data={}).serialize()

        existing_user = UserService().get_user_by_username(username)
        if existing_user and existing_user.id != user_id:
            return APIResponse(is_successful=False, error_message='User with username '+ username +' is existing.', data={}).serialize()

        existing_user = UserService().get_user_by_email(email)
        if existing_user and existing_user.id != user_id:
            return APIResponse(is_successful=False, error_message='User with email '+ email +' is existing.', data={}).serialize()

        with UserService() as service:

            u = None
            if user_id:
                u = service.get_user_by_id(user_id)
                u.first_name = first_name
                u.last_name = last_name
                u.email = email
                u.role = role
                u.status = status
                u.site_id = site_id

                service.save_one_user(u)
            else:
                password = string_utilities.generate_temporary_password(8)
                u = User(None, username, password, email, first_name, last_name, role, site_id)

                EmailService().send_email_to_new_user(u, password)

                service.save_one_user(u)

            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/site/delete', methods = ['DELETE'])
    @login_required
    def delete_site():
        site_id = int(request.get_data())

        with SiteService() as service:
            users = UserService().get_users_by_site(site_id)
            tenants = TenantService().get_tenant_by_site(site_id)
            tracking = ActivityTrackingService().get_activity_tracking_by_site(site_id)

            if users or tenants or tracking \
                or len(users) > 0 or len (tenants) > 0 or len(tracking) > 0:
                return APIResponse(is_successful=False, error_message='Cannot delete because there is some data linked with this site', data={}).serialize()


            service.delete_one_site(site_id)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/site/<_id>', methods = ['GET'])
    @login_required
    def get_site(_id):
        site_id = int(_id)

        with SiteService() as service:
            s = service.get_site_by_id(site_id)
            return s.serialize()

    @app.route('/api/site/save', methods = ['POST'])
    @login_required
    def save_site():
        site_dict = json.loads(request.get_data())

        site_id = int(site_dict['id']) if 'id' in site_dict and site_dict['id'] else None
        name = site_dict['name'] if 'name' in site_dict else None
        address_line1 = site_dict['address_line1'] if 'address_line1' in site_dict else None
        address_line2 = site_dict['address_line2'] if 'address_line2' in site_dict else None
        city = site_dict['city'] if 'city' in site_dict else None
        province = site_dict['province'] if 'province' in site_dict else None
        postal_code = site_dict['postal_code'] if 'postal_code' in site_dict else None
        manager_id = int(site_dict['manager_id']) if site_dict['manager_id'] else None
        notification_emails = site_dict['notification_emails'] if 'notification_emails' in site_dict else []

        if not name:
            return APIResponse(is_successful=False, error_message='Site name cannot be empty.', data={}).serialize()

        if not address_line1:
            return APIResponse(is_successful=False, error_message='Address Line 1 cannot be empty.', data={}).serialize()

        if not city:
            return APIResponse(is_successful=False, error_message='City cannot be empty.', data={}).serialize()

        if not postal_code:
            return APIResponse(is_successful=False, error_message='Postal Code cannot be empty.', data={}).serialize()

        if not province:
            return APIResponse(is_successful=False, error_message='Province cannot be empty.', data={}).serialize()

        if not string_utilities.validate_canada_postal_code(postal_code):
            return APIResponse(is_successful=False, error_message='Postal code does not match a valid format.', data={}).serialize()

        existing_site = SiteService().get_site_by_name(name)
        if existing_site and existing_site.id != site_id:
            return APIResponse(is_successful=False, error_message='Site with name '+name+' is already eixisting.', data={}).serialize()

        valid_notification_emails = []
        if notification_emails and len(notification_emails) > 0:
            for e in notification_emails:
                if not string_utilities.validate_email(e['notification_email']):
                    return APIResponse(is_successful=False, error_message='Email '+ e['notification_email'] +' does not match a valid format.', data={}).serialize()
                valid_notification_emails.append(e['notification_email'])

        with SiteService() as service:
            s = None
            if site_id:
                s = service.get_site_by_id(site_id)
                s.name = name
                s.address_line1 = address_line1
                s.address_line2 = address_line2
                s.city = city
                s.province = province
                s.postal_code = string_utilities.format_canada_postal_code(postal_code)
                s.manager_id = manager_id            
            else:
                formatted_postal_code = string_utilities.format_canada_postal_code(postal_code)
                s = Site(None, name, address_line1, address_line2, city, province, formatted_postal_code, manager_id)

            service.save_one_site(s, valid_notification_emails)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/tenant/delete', methods = ['DELETE'])
    @login_required
    def delete_tenant():
        tenant_id = int(request.get_data())

        with TenantService() as service:
            tracking = ActivityTrackingService().get_activity_tracking_by_tenant(tenant_id)
            if tracking or len(tracking) > 0:
                return APIResponse(is_successful=False, error_message='Cannot delete because there is some tracking linked with this tenant', data={}).serialize()

            service.delete_one_tenant(tenant_id)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/tenant/<_id>', methods = ['GET'])
    @login_required
    def get_tenant(_id):
        tenant_id = int(_id)

        with TenantService() as service:
            t = service.get_tenant_by_id(tenant_id)
            return t.serialize()

    @app.route('/api/tenant/save', methods = ['POST'])
    @login_required
    def save_tenant():
        tenant_dict = json.loads(request.get_data())

        tenant_id = int(tenant_dict['id']) if 'id' in tenant_dict and tenant_dict['id'] else None
        unique_name = tenant_dict['unique_name'] if 'unique_name' in tenant_dict else None
        unit = tenant_dict['unit'] if 'unit' in tenant_dict else None
        site_id = tenant_dict['site_id'] if 'site_id' in tenant_dict else None
        status = tenant_dict['status'] if 'status' in tenant_dict else None

        if not unique_name:
            return APIResponse(is_successful=False, error_message='Unique name cannot be empty.', data={}).serialize()

        if not string_utilities.validate_username(unique_name):
            return APIResponse(is_successful=False, error_message='Unique name must be 5-20 characters in length, and consists of alphanumeric characters and/or ._- only.', data={}).serialize()

        if not site_id:
            return APIResponse(is_successful=False, error_message='Site must be specified', data={}).serialize()

        existing_tenant = TenantService().get_tenant_by_unique_name(unique_name, site_id)
        if existing_tenant and existing_tenant.id != tenant_id:
            return APIResponse(is_successful=False, error_message='Tenant with unique name '+unique_name+' is existing in the specified site. ', data={}).serialize()

        with TenantService() as service:
            t = None
            if tenant_id:
                t = service.get_tenant_by_id(tenant_id)
                t.unique_name = unique_name
                t.unit = unit
                t.site_id = site_id
                t.status = status

            else:
                t = Tenant(None, unique_name, unit, site_id)

            service.save_one_tenant(t)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/activity_category/delete', methods = ['DELETE'])
    @login_required
    def delete_activity_category():
        activity_category_id = int(request.get_data())

        with ActivityCategoryService() as service:
            tracking = ActivityTrackingService().get_activity_tracking_by_category(activity_category_id)
            if tracking or len(tracking) > 0:
                return APIResponse(is_successful=False, error_message='Cannot delete because there is some tracking linked with this category', data={}).serialize()

            service.delete_one_activity_category(activity_category_id)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/activity_category/<_id>', methods = ['GET'])
    @login_required
    def get_activity_category(_id):
        activity_category_id = int(_id)

        with ActivityCategoryService() as service:
            c = service.get_activity_category_by_id(activity_category_id)
            return c.serialize()

    @app.route('/api/activity_category/save', methods = ['POST'])
    @login_required
    def save_activity_category():
        activity_category_dict = json.loads(request.get_data())

        activity_category_id = int(activity_category_dict['id']) if 'id' in activity_category_dict and activity_category_dict['id'] else None
        code = activity_category_dict['code'] if 'code' in activity_category_dict else None
        description = activity_category_dict['description'] if 'description' in activity_category_dict else None
        alert_level = activity_category_dict['alert_level'] if 'alert_level' in activity_category_dict else None

        if not code:
            return APIResponse(is_successful=False, error_message='Code cannot be empty.', data={}).serialize()

        if not description:
            return APIResponse(is_successful=False, error_message='Description cannot be empty.', data={}).serialize()

        c = ActivityCategoryService().get_activity_category_by_code(code)
        if c and activity_category_id != c.id :
            return APIResponse(is_successful=False, error_message='Code '+ code +' is existing.', data={}).serialize()

        if not alert_level:
            return APIResponse(is_successful=False, error_message='Alert level must be specified', data={}).serialize()

        with ActivityCategoryService() as service:
            t = None
            if activity_category_id:
                t = service.get_activity_category_by_id(activity_category_id)
                t.code = code
                t.description = description
                t.alert_level = alert_level

            else:
                t = ActivityCategory(None, code, description, alert_level)

            service.save_one_activity_category(t)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/activity_tracking/delete', methods = ['DELETE'])
    @login_required
    def delete_activity_tracking():
        activity_tracking_id = int(request.get_data())

        with ActivityTrackingService() as service:
            service.delete_one_activity_tracking(activity_tracking_id)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/activity_tracking/<_id>', methods = ['GET'])
    @login_required
    def get_activity_tracking(_id):
        activity_tracking_id = int(_id)

        with ActivityTrackingService() as service:
            c = service.get_activity_tracking_by_id(activity_tracking_id)
            return c.serialize()

    @app.route('/api/activity_tracking/upload', methods = ['POST'])
    @login_required
    def upload_activity_tracking():
        if request.files and 'record_file' in request.files:
            df = pd.DataFrame(columns=['Site', 'Tenant', 'Activity Category', 'Date', 'Time', 'Comments'])
            try:
                df = pd.read_csv(request.files['record_file'], dtype={
                    'Site':str,
                    'Tenant': str,
                    'Activity Category': str,
                    'Date': str,
                    'Time': str,
                    'Comments': str}
                )
            except:
                return APIResponse(is_successful=False, error_message='The uploaded file is not in correct format.', data={}).serialize()

            site_service = SiteService()
            tenant_service = TenantService()
            activity_category_service = ActivityCategoryService()
            activity_tracking_service = ActivityTrackingService()

            save_objs = []
            for index, row in df.iterrows():
                site_name = str(row['Site']).strip() if not pd.isnull(row['Site']) else None
                tenant_unique_name = str(row['Tenant']).strip() if not pd.isnull(row['Tenant']) else None
                activity_category_code = str(row['Activity Category']).strip() if not pd.isnull(row['Activity Category']) else None
                date_str = str(row['Date']).strip() if not pd.isnull(row['Date']) else None
                time_str = str(row['Time']).strip() if not pd.isnull(row['Time']) else None
                comments = str(row['Comments']).strip() if not pd.isnull(row['Comments']) else None

                if not site_name or site_name == "":
                    return APIResponse(is_successful=False, error_message='Site must be specified at record '+str(index+1), data={}).serialize()
                if not tenant_unique_name or tenant_unique_name == "":
                    return APIResponse(is_successful=False, error_message='Tenant must be specified at record '+str(index+1), data={}).serialize()
                if not activity_category_code or activity_category_code == "":
                    return APIResponse(is_successful=False, error_message='Activity category must be specified at record '+str(index+1), data={}).serialize()
                if not date_str or date_str == "":
                    return APIResponse(is_successful=False, error_message='Date must be specified at record '+str(index+1), data={}).serialize()

                site_obj = site_service.get_site_by_name(site_name)
                if not site_obj:
                    return APIResponse(is_successful=False, error_message='Site at record '+str(index+1)+' cannot be found', data={}).serialize()

                if current_user.role == prj_constants.USER_ROLE_SITE_MANAGER:
                    available_site_ids = [s.id for s in site_service.get_site_by_manager(current_user.id)]
                    if site_obj.id not in available_site_ids:
                        return APIResponse(is_successful=False, error_message='You are not managing the site at record '+str(index+1), data={}).serialize()
                elif current_user.role == prj_constants.USER_ROLE_USER:
                    if site_obj.id != current_user.site_id:
                        return APIResponse(is_successful=False, error_message='You are not managing the site at record '+str(index+1), data={}).serialize()

                tenant_obj = tenant_service.get_tenant_by_unique_name(tenant_unique_name, site_obj.id)
                if not tenant_obj:
                    return APIResponse(is_successful=False, error_message='Tenant at record '+str(index+1)+' cannot be found', data={}).serialize()

                activity_category_obj = activity_category_service.get_activity_category_by_code(activity_category_code)
                if not activity_category_obj:
                    return APIResponse(is_successful=False, error_message='Activity Category at record '+str(index+1)+' cannot be found', data={}).serialize()
                if not string_utilities.convert_yyyymmdd_str_to_int(date_str):
                    return APIResponse(is_successful=False, error_message='Invalid date format at record '+str(index+1), data={}).serialize()
                if not time_str or string_utilities.convert_hh24miss_str_to_int(time_str) == None:
                    return APIResponse(is_successful=False, error_message='Invalid time format at record '+str(index+1), data={}).serialize()

                save_objs.append(
                    ActivityTracking(
                        None,
                        site_obj.id,
                        tenant_obj.id,
                        activity_category_obj.id,
                        string_utilities.convert_yyyymmdd_str_to_int(date_str),
                        string_utilities.convert_hh24miss_str_to_int(time_str) if time_str else None,
                        comments)
                )

            if len(save_objs) == 0:
                return APIResponse(is_successful=False, error_message='No record is found in the uploaded file.', data={}).serialize()

            activity_tracking_service.save_many_activity_tracking(save_objs)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

        return APIResponse(is_successful=False, error_message='Cannot find the uploaded file in the HTTP request.', data={}).serialize()

    @app.route('/api/activity_tracking/save', methods = ['POST'])
    @login_required
    def save_activity_tracking():
        activity_tracking_dict = json.loads(request.get_data())

        activity_tracking_id = int(activity_tracking_dict['id']) \
            if 'id' in activity_tracking_dict and activity_tracking_dict['id'] else None
        site_id = int(activity_tracking_dict['site_id']) \
            if 'site_id' in activity_tracking_dict and activity_tracking_dict['site_id'] else None
        tenant_id = int(activity_tracking_dict['tenant_id']) \
            if 'tenant_id' in activity_tracking_dict and activity_tracking_dict['tenant_id'] else None
        activity_category_id = int(activity_tracking_dict['activity_category_id']) \
            if 'activity_category_id' in activity_tracking_dict and activity_tracking_dict['activity_category_id'] else None
        date_of_record = activity_tracking_dict['date_of_record'] if 'date_of_record' in activity_tracking_dict else None
        time_of_record = activity_tracking_dict['time_of_record'] if 'time_of_record' in activity_tracking_dict else None
        comments = activity_tracking_dict['comments'] if 'comments' in activity_tracking_dict else None

        if not site_id:
            return APIResponse(is_successful=False, error_message='Site must be specified', data={}).serialize()

        if not tenant_id:
            return APIResponse(is_successful=False, error_message='Tenant must be specified', data={}).serialize()

        if not activity_category_id:
            return APIResponse(is_successful=False, error_message='Activity category must be specified', data={}).serialize()

        if not date_of_record:
            return APIResponse(is_successful=False, error_message='Date must be specified.', data={}).serialize()

        if not string_utilities.convert_yyyymmdd_str_to_int(date_of_record):
            return APIResponse(is_successful=False, error_message='Invalid date format.', data={}).serialize()

        if not time_of_record or string_utilities.convert_hh24miss_str_to_int(time_of_record) == None:
            return APIResponse(is_successful=False, error_message='Invalid time format.', data={}).serialize()    

        with ActivityTrackingService() as service:
            t = None
            if activity_tracking_id:
                t = service.get_activity_tracking_by_id(activity_tracking_id)
                t.site_id = site_id
                t.tenant_id = tenant_id
                t.activity_category_id = activity_category_id
                t.date_of_record = string_utilities.convert_yyyymmdd_str_to_int(date_of_record)
                t.time_of_record = string_utilities.convert_hh24miss_str_to_int(time_of_record) if time_of_record else None
                t.comments = comments

            else:
                t = ActivityTracking(None
                , site_id
                , tenant_id
                , activity_category_id
                , string_utilities.convert_yyyymmdd_str_to_int(date_of_record)
                , string_utilities.convert_hh24miss_str_to_int(time_of_record) if time_of_record else None
                , comments)

            service.save_one_activity_tracking(t)
            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    @app.route('/api/system_configuration/<_id>', methods = ['GET'])
    @login_required
    def get_system_configuration(_id):
        system_configuration_id = int(_id)

        with SystemConfigurationService() as service:
            t = service.get_configuration_by_id(system_configuration_id)
            return t.serialize()

    @app.route('/api/system_configuration/save', methods = ['POST'])
    @login_required
    def save_system_configuration():
        system_configuration_dict = json.loads(request.get_data())

        system_configuration_id = int(system_configuration_dict['id']) if 'id' in system_configuration_dict and system_configuration_dict['id'] else None
        conf_value = system_configuration_dict['conf_value'] if 'conf_value' in system_configuration_dict else None
        description = system_configuration_dict['description'] if 'description' in system_configuration_dict else None

        if not conf_value:
            return APIResponse(is_successful=False, error_message='Configuration''s value cannot be empty.', data={}).serialize()

        with SystemConfigurationService() as service:
            c = service.get_configuration_by_id(system_configuration_id)
            if not c:
                return APIResponse(is_successful=False, error_message='Cannot find the system configuration.', data={}).serialize()

            if c.validation_regex and not string_utilities.match_regex(c.validation_regex, conf_value):
                return APIResponse(is_successful=False, error_message='Configuration''s value is not in the right format.', data={}).serialize()

            c.conf_value = conf_value
            c.description = description
            service.save_one_configuration(c)

            return APIResponse(is_successful=True, error_message='', data={}).serialize()

    #session.clear()
    
    return app

if __name__ == "__main__":
    _app = create_app()
    _app.run()