import pdb

from clinicapp import app, login
from flask import render_template, redirect, request, jsonify
from flask_login import login_user, login_required, logout_user
from flask_admin import expose
import hashlib
import cloudinary.uploader
from flask import url_for, json, session
import datetime
import uuid


@app.route("/")
def homepage():
    if current_user.is_authenticated:
        if current_user.user_role == UserRole.NURSE:
            return redirect('/nurse-view')
        elif current_user.user_role == UserRole.DOCTOR:
            return redirect('/doctor-view')
        else:
            return redirect('/admin')
    comments = utils.get_comment()
    return render_template('index.html', comments=comments)

@app.route("/return-admin")
def return_admin_page():
    return redirect('/admin')


@app.route("/admin/login", methods=['POST', 'GET'])
def login_admin():
    if request.method == "POST":
        username = request.form.get('userN')
        password = request.form.get('passW', '')
        password = str(hashlib.md5(password.encode("utf-8")).hexdigest())
        user = User.query.filter(User.username == username, User.password == password).first()
        if user:
            login_user(user=user)
    return redirect('/admin')

@expose('/')
@app.route('/user')
def edit_profile():
    return redirect('/admin/user')
@login.user_loader
def get_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def common_response():
    return {
        "sex": check_sex(current_user),
        "date_now": datetime.datetime.now().strftime('%Y-%m-%d')
    }


@app.route('/employee-login', methods = ['post', 'get'])
def employee_login():
    error_ms = ''
    if current_user.is_authenticated:
        if current_user.user_role == UserRole.NURSE:
            return redirect('/nurse-view')
        elif current_user.user_role == UserRole.DOCTOR:
            return redirect('/doctor-view')
        else:
            return redirect('/admin')
    else:
        if request.method.__eq__('POST'):
            username = request.form.get('username')
            password = request.form.get('password')
            user = check_login(username=username, password=password)
            if user:
                login_user(user=user)
                if user.user_role == UserRole.ADMIN:
                    return redirect('/admin')
                elif user.user_role == UserRole.NURSE:
                    return redirect('/nurse-view')
                return redirect('/doctor-view')
            else:
                error_ms = "Sai tên đăng nhập hoặc mật khẩu!!!"
        return render_template('login-user.html', error_ms=error_ms)

@app.route('/doctor-view')
@login_required
def doctor_view():
    error_ms = request.args.get('error_ms')
    return render_template('doctor-view.html',error_ms = error_ms )

@app.route('/nurse-view')
@login_required
def nurse_view():
    error_ms = request.args.get('error_ms')
    return render_template('nurse-view.html',error_ms = error_ms)

@app.route("/user-logout")
def user_logout():
    logout_user()
    return redirect("/")

@app.route('/nurse-view/medical-register')
@login_required
def medical_register():
    return render_template('medical_register.html')

@app.route('/nurse-view/make-medical-list')
@login_required
def make_medical_list():
    d = request.args.get('date')
    temp = d
    if not d:
        temp = utils.get_last_date_of_exam()
        d = '-'.join([temp.get('year'), temp.get('month'), temp.get('day')])
    return render_template('make_medical_list.html', last_date=temp,\
                           med_list=utils.get_patient_in_exam(d), status=utils.get_status_of_exam(d))

@app.route('/nurse-view/pay-the-bill')
@login_required
def pay_the_bill():
    d = request.args.get('date')
    return render_template('pay-the-bill.html', bill=utils.get_bill_from_medicall_bill_in_day(exam_date=d))

@app.route('/nurse-view/pay-the-bill/<int:bill_id>')
@login_required
def detail_pay_the_bill(bill_id):
    bill = utils.get_bill(bill_id)
    return render_template('detail-pay-the-bill.html', bill=bill)

@app.route('/api/pay-bill', methods=['post'])
@login_required
def pay():
    data = request.json
    id = data.get('id')
    if id:
        if pay_bill(id):
            return jsonify({'code': 200})
    return jsonify({'code': 400})


@app.route('/api/momo_pay_status')
def get_momo_pay_status():
    data = request.json
    pass

@app.route('/api/pay_with_momo', methods=['post'])
@login_required
def pay_momo():
    data = request.json
    id = data.get('id')
    amount = data.get('amount')
    re_url = data.get('current_url')
    if id and amount and re_url:
        id = "Clinic-bill-test-" + str(id) + "-" + str(datetime.date.today())
        pay_url = pay_bill_with_momo(id, amount, re_url)
        if pay_url:
            return jsonify({'code': 200, 'pay_url': pay_url})
    return jsonify({'code': 400})


@app.route('/api/create-exam', methods=['post'])
@login_required
def create():
    data = request.json
    id = data.get('id')
    if id:
        if change_status_examination(id):
            return jsonify({'code': 200})
    return jsonify({'code': 400})

@app.route('/api/create-medical-bill', methods=['post'])
@login_required
def create_medical_bill_by_doctor():
    data = request.json
    user_id = data.get('user_id')
    patient_id = data.get('patient_id')
    exam_date = data.get('exam_date')
    medicine = data.get('medicine')
    diagnosis = data.get('diagnosis')
    symptom = data.get('symptom')
    check = 0
    if patient_id and user_id and exam_date:
        for unit in medicine:
            if unit and medicine[unit]["quantity"]:
                check = check + 1
                if check == 1:
                    med_bill = create_medical_bill(user_id, patient_id, exam_date, diagnosis, symptom)
                if check >= 1:
                    temp = utils.create_medical_bill_detail(med_bill.id, unit, medicine[unit]["quantity"],\
                                                        medicine[unit]["use"])
                    if not temp:
                        return jsonify({'code': 400})
        temp = utils.get_cost()
        if check == 0:
            return jsonify({'code': 400})
        b = utils.get_medical_bill_value(med_bill.id)
        bill = Bill(medical_bill_id=b[0], value=b[1] + temp)
        try:
            db.session.add(bill)
            db.session.commit()
            return jsonify({'code': 200})
        except:
            return jsonify({'code': 400})
    return jsonify({'code': 400})

@app.route('/doctor-view/make-a-medical-bill')
@login_required
def make_a_medical_bill():
    d = request.args.get('date')
    temp = d
    if not d:
        temp = utils.get_last_date_of_exam(doctor=True)
        if temp:
            d = '-'.join([temp.get('year'), temp.get('month'), temp.get('day')])
        else:
            temp = {}
    pa = utils.get_patient_in_exam(exam_date=d, doctor=True)
    pati = utils.get_patient_and_medical_bill_in_exam(pa)
    return render_template('make_a_medical_bill.html', last_date=temp, pati=pati)

@app.route('/doctor-view/make-a-medical-bill/<int:patient_id>/<string:date>')
@login_required
def detail_make_a_medical_bill(patient_id, date):
    patient = utils.get_patient(patient_id)
    temp = patient[0]
    medicine = utils.get_medicine()
    return render_template('detail-make-a-medical-bill.html', patient=temp, date=date, medicine=medicine)

@app.route('/api/get_medicine', methods=['post'])
@login_required
def get_list_medicine_unit():
    return jsonify(utils.get_medicine_json())

@app.route('/api/get_medicine_unit_quantity', methods=['post'])
@login_required
def get_quantity_medicine_unit():
    return jsonify(utils.get_quantity_medicine_unit_json())


@app.route('/change-info-user', methods = ['post', 'get'])
def change_info_user():
    if request.method.__eq__('POST'):
        avatar = request.files.get('avatar')
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        sex = request.form.get('sex_of_user')
        day_of_birth = request.form.get('dob')
        phone = request.form.get('phone')
        password = request.form.get('password')
        new_password = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        error_ms = check_info_for_error_ms(current_user = current_user,avatar = avatar, name= name,\
                                       username=username,email = email, sex = sex,day_of_birth= day_of_birth,\
                                       phone=phone,password = password,new_password = new_password,confirm = confirm)
    return redirect(url_for(check_role_for_render(current_user), error_ms = error_ms))


@app.route('/api/check-phone-number', methods = ['post'])
def api_check_phone_number():
    data = request.json
    phone_number = data.get('phone_number')
    if not phone_number.isdigit():
        return jsonify({'code': 400,
                        'phone_number': phone_number,
                        'error_ms': 'Nhập sai định dạng số điện thoại!!!'})

    patient = check_phone_number_of_patient(phone_number=phone_number)
    if patient:
        return jsonify({'code': 200,
                        'first_name': patient.first_name,
                        'last_name': patient.last_name,
                        'sex': patient.sex.value,
                        'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d')})
    return jsonify({'code': 300,
                        'phone_number': phone_number})


@app.route('/api/medical-register', methods = ['post'])
def api_medical_register():
    data = request.json
    phone_number = data.get('phone_number')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    sex = data.get('sex')
    date_of_birth = data.get('date_of_birth')
    date_of_exam = data.get('date_of_exam')
    final = medical_register(phone_number=phone_number,first_name= first_name,\
                             last_name=last_name,sex= sex,date_of_birth= date_of_birth, date_of_exam= date_of_exam)
    return final
@app.route('/api/comment', methods=['post'])
def add_comment():
    data = request.json
    content_comment = data.get('content_comment')
    patient_comment = data.get('patient_comment')
    star_comment = data.get('star_comment')

    try:
        c = utils.add_comment(patient_comment=patient_comment,content_comment=content_comment,star_comment=star_comment)
    except:
        return {'status': 404,'err_msg':'Chuong trinh bi loi'}

    return jsonify({'status':201,'comment':{
        'patient_comment': c.patient_comment,
        'content_comment': c.content_comment,
        'star_comment': c.star_comment
    }})

if __name__ == "__main__":
    from clinicapp.admin import *
    app.run(debug=True)



