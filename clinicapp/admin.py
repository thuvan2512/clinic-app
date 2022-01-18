from flask_admin import BaseView, expose,AdminIndexView
from flask import redirect, request
from flask_admin import Admin
from clinicapp import app, db, utils
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user, login_required
from clinicapp.models import *
from clinicapp.utils import *
from datetime import date

class BackHome(BaseView):
    @expose('/')
    def index(self):
        return redirect('/')
    def is_accessible(self):
        return current_user.is_authenticated==False


class LogoutView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated
    @expose("/")
    def index(seft):
        logout_user()
        return redirect('/admin')

class MedicalBillView(ModelView):
    can_export = True
    edit_modal = True
    details_modal = True
    column_filters = ['create_date']
    column_labels = {
        'create_date':"Ngày lập phiếu khám",
        'diagnosis': "Chuẩn đoán",
        'symptom': "Triệu chứng"
    }
    column_exclude_list = ['user', 'patient']
    column_searchable_list = ['diagnosis','symptom']
    form_columns = ('create_date','user','diagnosis','symptom')
    can_view_details = True
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MedicineView(ModelView):
    can_export = True
    edit_modal = True
    details_modal = True
    column_filters = ['name']
    column_labels = {
        'name':"Tên thuốc",
        'effect': "Tác dụng",
        'medicine_units': 'Đơn vị tính'
    }
    column_searchable_list = ['name','effect']
    form_columns = ('name','effect')
    column_list = ['name', 'effect', 'medicine_units']
    can_view_details = True
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MedicineUnitView(ModelView):
    column_labels = {
        'price':"Giá bán",
        'quantity': "Số lượng",
        'medicine': 'Tên thuốc',
        'unit_tag':'Đơn vị'
    }
    can_export = True
    edit_modal = True
    details_modal = True
    form_columns = ['price', 'medicine', 'unit_tag','quantity']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UnitTagView(ModelView):
    column_labels = {
        'name':"Đơn vị"
    }
    can_export = True
    form_columns = ['name']
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UserView(ModelView):
    can_export = True
    edit_modal = True
    details_modal = True
    column_filters = ['name','user_role','joined_date']
    column_labels = {
        'name':"Tên",
        'username': "Tên đăng nhập",
        'password': "Mật khẩu",
        'joined_date': "Ngày khởi tạo",
        'user_role': "Vai trò",
        'avatar':'Ảnh đại diện',
        'date_of_birth':'Ngày sinh',
        'sex': 'Giới tính',
        'phone_number': 'Số điện thoại'
    }
    column_exclude_list = ['avatar','medical_bills', 'password']
    column_searchable_list = ['name','username','joined_date']
    form_columns = ('name','username','sex','date_of_birth','user_role', 'phone_number', 'email', 'password')
    can_view_details = True
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class Profit_stats_view(BaseView):
    @expose('/')
    @login_required
    def index(self):
        month_year = request.args.get('month')
        month = None
        year = None
        temp = []
        if month_year:
            temp = month_year.split('-')
            month = temp[1]
            year = temp[0]
        return self.render('admin/profit_stats.html', stats=utils.stat_profit(month=month, year=year),\
                           total_profit=utils.get_total_bill_in_month(month=month, year=year),\
                           last_m_y=utils.get_last_month_in_bill())
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class Medicine_stats_view(BaseView):
    @expose('/')
    @login_required
    def index(self):
        month_year = request.args.get('month')
        month = None
        year = None
        temp = []
        if month_year:
            temp = month_year.split('-')
            month = temp[1]
            year = temp[0]
        return self.render('admin/medicine_stats.html', stats=utils.stat_medicine(month=month, year=year),\
                           last_m_y=utils.get_last_month_in_bill())
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', dsqtv = get_list_admin(current_user), role = check_role(current_user))

class RegulationsView(ModelView):
    column_labels = {
        'cost':"Giá khám bệnh",
        'slot': "Suất khám",
        'active': "Duyệt"
    }
    can_export = True
    can_create = False
    can_delete = False
    edit_modal = True
    details_modal = True
    can_view_details = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin=Admin(app=app, name='Quản Trị Hệ Thống', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(UserView(User, db.session,name="Tài Khoản"))
admin.add_view(MedicalBillView(Medical_bill, db.session,name="Phiếu Khám"))
admin.add_view(MedicineView(Medicine, db.session,name="Các loại thuốc", category="Quản lý thuốc"))
admin.add_view(Profit_stats_view(name="Doanh thu", category="Thống kê"))
admin.add_view(Medicine_stats_view(name="Tần suất sử dụng thuốc", category="Thống kê"))
admin.add_view(MedicineUnitView(Medicine_unit, db.session,name="Đơn vị của từng loại thuốc", category="Quản lý thuốc"))
admin.add_view(UnitTagView(Unit_tag, db.session, name="Đơn vị thuốc", category="Quản lý thuốc"))
admin.add_view(BackHome(name="Trở Về"))
admin.add_view(RegulationsView(Other, db.session, name="Quy định"))
admin.add_view(LogoutView(name="Đăng Xuất"))
