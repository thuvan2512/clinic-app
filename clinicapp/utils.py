import datetime
from flask import jsonify
from clinicapp.models import Medical_bill, Medicine, Medicine_unit, Medical_bill_detail, Bill, Unit_tag, User, UserRole,\
    Examination, Patient, Exam_patient, Sex, Other,Comment
from clinicapp import db
from sqlalchemy import func, extract, desc, alias, update
from twilio.rest import Client
import hashlib, datetime
import cloudinary.uploader
import urllib.request
import uuid
import hmac
import json


def get_medical_bill_value(mb_id=None):
    bills = db.session.query(Medical_bill_detail.medical_bill_id,
                             func.sum(Medical_bill_detail.quantity * Medicine_unit.price)) \
                            .join(Medicine_unit, Medicine_unit.id == Medical_bill_detail.medicine_unit_id, isouter=True) \
                            .group_by(Medical_bill_detail.medical_bill_id)
    if mb_id:
        bills = bills.filter(Medical_bill_detail.medical_bill_id.__eq__(int(mb_id)))
        return bills.first()
    return bills.all()

def get_bill_with_create_date(cd=None, id=None):
    bills = db.session.query(Medical_bill.create_date, func.sum(Bill.value))\
                    .join(Bill, Medical_bill.id == Bill.medical_bill_id, isouter=True)\
                    .group_by(Medical_bill.create_date)
    if cd:
        temp = cd.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        bills = bills.filter(extract('day', Medical_bill.create_date) == day,\
                             extract('month', Medical_bill.create_date) == month,\
                             extract('year', Medical_bill.create_date) == year)
    return bills.all()

def get_last_month_in_bill():
    last_month_in_bill = db.session.query(Medical_bill.create_date).order_by(Medical_bill.create_date.desc()).first()
    last_month = last_month_in_bill[0].strftime("%m")
    last_year = last_month_in_bill[0].strftime("%Y")
    return {'month': last_month, 'year': last_year}

def stat_profit(month=None, year=None):
    bills = db.session.query(Medical_bill.create_date, func.sum(Bill.value), func.count(Medical_bill.id)) \
                    .join(Bill, Medical_bill.id == Bill.medical_bill_id) \
                    .group_by(Medical_bill.create_date)
    if not month or not year:
        tempe = get_last_month_in_bill()
        month = tempe.get('month')
        year = tempe.get('year')
    if month and year:
        if type(month) is not int and month is not None:
            month = int(month)
        if type(year) is not int and year is not None:
            year = int(year)
        bills = bills.filter(extract('month', Medical_bill.create_date) == month, \
                                            extract('year', Medical_bill.create_date) == year)
    if len(bills.all()) <= 0:
        return None
    return bills.all()

def get_total_bill_in_month(month=None, year=None):
    tempe = stat_profit(month, year)
    total_profit=0
    if tempe:
        for t in tempe:
            total_profit += t[1]
    return total_profit

def stat_medicine(month=None, year=None):
    med_unit = db.session.query(Medicinename, Unit_tag.name, func.sum(Medical_bill_detail.quantity),\
                                Medicine_unit.unit_id, \
                                func.count(Medical_bill_detail.medicine_unit_id), Medical_bill.create_date) \
                                .join(Unit_tag, Unit_tag.id == Medicine_unit.unit_id) \
                                .join(Medicine, Medicine.id == Medicine_unit.medicine_id) \
                                .join(Medical_bill_detail, Medical_bill_detail.medicine_unit_id == Medicine_unit.id) \
                                .join(Medical_bill, Medical_bill_detail.medical_bill_id == Medical_bill.id) \
                                .group_by(Medicine.name, Unit_tag.name, Medical_bill.create_date)
    if not month or not year:
        tempe = get_last_month_in_bill()
        month = tempe.get('month')
        year = tempe.get('year')
    if month and year:
        if type(month) is not int and month is not None:
            month = int(month)
        if type(year) is not int and year is not None:
            year = int(year)
        med_unit = med_unit.filter(extract('month', Medical_bill.create_date) == month, \
                                    extract('year', Medical_bill.create_date) == year)
    if len(med_unit.all()) <= 0:
        return None
    return med_unit.all()

def count_patient_in_exam(exam_date=None):
    count = db.session.query(func.count(Exam_patient.c.patient_id)) \
                            .join(Examination, Examination.id == Exam_patient.c.exam_id)
    if exam_date:
        temp = exam_date.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        count = count.filter(extract('day', Examination.date) == day,\
                                        extract('month', Examination.date) == month, \
                                        extract('year', Examination.date) == year)
    if len(count.all()) <= 0:
        return None
    return count.first()[0]

def get_patient_in_exam(exam_date=None, doctor=False, sub=None):
    pati = db.session.query(Examination.date, Patient.last_name, Patient.first_name, Patient.sex, Patient.date_of_birth,\
                            Patient.phone_number, Patient.id, Examination.id, Examination.apply)\
                            .join(Exam_patient, Exam_patient.c.patient_id == Patient.id) \
                            .join(Examination, Examination.id == Exam_patient.c.exam_id)
    if exam_date:
        temp = exam_date.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        pati = pati.filter(extract('day', Examination.date) == day, \
                                        extract('month', Examination.date) == month, \
                                        extract('year', Examination.date) == year)
        if doctor:
            pati = pati.filter(Examination.apply.__eq__(True))
        if len(pati.all()) <= 0:
            return None
        if sub:
            return pati
        else:
            return pati.all()
    else:
        return None

def get_last_date_of_exam(doctor=False):
    temp = db.session.query(Examination.date, Examination.apply).order_by(Examination.date.desc())
    if doctor:
        temp = temp.filter(Examination.apply.__eq__(True)).first()
    else:
        temp = temp.first()
    if temp:
        day = temp[0].strftime("%d")
        month = temp[0].strftime("%m")
        year = temp[0].strftime("%Y")
        return {'day': day, 'month': month, 'year': year}
    else:
        return None

def get_status_of_exam(exam_date=None):
    if exam_date:
        temp = exam_date.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        status = db.session.query(Examination.apply, Examination.date)\
                                .filter(extract('day', Examination.date) == day, \
                                        extract('month', Examination.date) == month, \
                                        extract('year', Examination.date) == year)
        if len(status.all()) > 0:
            return status.first()[0]
        else:
            return False
    else:
        return None

def change_status_examination(exam_id=None):

    if exam_id:
        if send_sms_to_patient(exam_id) == False:
            return False
        Examination.query.filter_by(id=int(exam_id)).update(dict(apply=True))
        db.session.commit()
        return True
    else:
        return False

def get_medical_bill_of_patient_in_an_exam(pte_id=None, exam_date=None, sub=None):
    mb = db.session.query(Patient.last_name, Patient.first_name, Medical_bill.create_date, Medical_bill.id) \
                        .join(Medical_bill, Patient.id == Medical_bill.patient_id)
    if pte_id:
        mb = mb.filter(Patient.id.__eq__(int(pte_id)))
    if exam_date:
        temp = exam_date.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        mb = mb.filter(extract('day', Medical_bill.create_date) == day,\
                                extract('month', Medical_bill.create_date) == month,\
                                extract('year', Medical_bill.create_date) == year)
    if len(mb.all()) > 0:
        if sub:
            return mb
        else:
            return mb.all()
    else:
        return None

def get_patient_and_medical_bill_in_exam(pati=None):
    if not pati:
        return None
    total = []
    for p in pati:
        temp = []
        day = p[0].strftime("%d")
        month = p[0].strftime("%m")
        year = p[0].strftime("%Y")
        d = '-'.join([year, month, day])
        temp = list(p)
        check = get_medical_bill_of_patient_in_an_exam(pte_id=p[6], exam_date=d)
        if check:
            temp.append(True)
        else:
            temp.append(False)
        total.append(tuple(temp))
    return total

def get_bill_from_medicall_bill_in_day(exam_date=None):
    bills = db.session.query(Medical_bill.create_date, Patient.last_name, Patient.first_name,\
                             Patient.date_of_birth, Bill.value, Bill.pay,Bill.id)\
                            .join(Bill, Bill.medical_bill_id == Medical_bill.id)\
                            .join(Patient, Medical_bill.patient_id == Patient.id)\
                            .order_by(Medical_bill.create_date.desc())
    if exam_date:
        temp = exam_date.split('-')
        year = temp[0]
        month = temp[1]
        day = temp[2]
        bills = bills.filter(extract('day', Medical_bill.create_date) == day, \
                       extract('month', Medical_bill.create_date) == month, \
                       extract('year', Medical_bill.create_date) == year)
    if len(bills.all()) > 0:
        return bills.all()
    else:
        return None

def get_patient(pte_id=None):
    patient = db.session.query(Patient)
    if pte_id:
        patient = patient.filter_by(id=int(pte_id))
    return patient

def get_exam_by_id(exam_id=None, exam_date=None):
    exam = db.session.query(Examination)
    if exam_id:
        exam = exam.filter_by(id=int(exam_id))
    if not exam_id and exam_date:
        exam = exam.filter_by(date=exam_date)
    return exam

def check_patient_in_an_exam(patient, list_patient):
    for p in list_patient:
        if patient.id.__eq__(p[6]):
            return True
    return False

def get_medicine(medicine_id=None):
    medicine = db.session.query(Medicine)
    if medicine_id:
        medicine = medicine.filter_by(id=int(medicine_id))
    return medicine

def get_medicine_unit(medicine_unit_id=None):
    medicine_unit = db.session.query(Medicine_unit)
    if medicine_unit_id:
        medicine_unit = medicine_unit.filter_by(id=int(medicine_unit_id))
    return medicine_unit

def get_tag(unit_tag_id=None):
    unit_tag = db.session.query(Unit_tag)
    if unit_tag_id:
        unit_tag = unit_tag.filter_by(id=int(unit_tag_id))
    return unit_tag

def get_medicine_json():
    total = {}
    medicine = get_medicine()
    for med in medicine:
        total[med.id] = {"name": med.name, "unit": {}}
        for med_unit in med.medicine_units:
            total[med.id]["unit"][med_unit.id] = {"tag": get_tag(med_unit.unit_id)[0].name, "price": med_unit.price,\
                                                  "quantity": med_unit.quantity}
    return total

def get_quantity_medicine_unit_json():
    total = {}
    medicine_unit = get_medicine_unit()
    for med_unit in medicine_unit:
        total[med_unit.id] = {"quantity": med_unit.quantity}
    return total


def create_patient(first_name, last_name, sex, date_of_birth, phone_number):
    temp = date_of_birth.split('-')
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    if int(sex) == 1:
        sex = Sex.MALE
    elif int(sex) == 2:
        sex = Sex.FEMALE
    else:
        sex = Sex.UNSPECIFIED
    patient = Patient(first_name=first_name, last_name=last_name, sex=sex, \
                      date_of_birth=datetime.datetime(year, month, day), phone_number=phone_number)
    try:
        db.session.add(patient)
        db.session.commit()
        return patient
    except:
        return None

def create_exam(user_id, exam_date):
    temp = exam_date.split('-')
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    exam = Examination(user_id=int(user_id), date=datetime.datetime(year, month, day))
    try:
        db.session.add(exam)
        db.session.commit()
        return exam
    except:
        return None

def register_into_examination(patient_id, exam_date):
    temp = exam_date.split('-')
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    exam = get_exam_by_id(exam_date=datetime.datetime(year, month, day)).first()
    patient = get_patient(patient_id).first()
    if not exam:
        exam = create_exam(user_id=1, exam_date=exam_date)
    exam.patients.append(patient)
    try:
        db.session.add(exam)
        db.session.commit()
        return True
    except:
        return False

def create_medical_bill(user_id, patient_id, exam_date, diagnosis, symptom):
    temp = exam_date.split('-')
    year = int(temp[0])
    month = int(temp[1])
    day = int(temp[2])
    mb = Medical_bill(user_id=user_id, diagnosis=diagnosis, symptom=symptom,\
                      create_date=datetime.datetime(year, month, day), patient_id=patient_id)
    try:
        db.session.add(mb)
        db.session.commit()
        return mb
    except:
        return None

def create_medical_bill_detail(medical_bill_id, medicine_unit_id, quantity, use):
    mbd = Medical_bill_detail(medical_bill_id=int(medical_bill_id), medicine_unit_id=int(medicine_unit_id),\
                              quantity=int(quantity), use=use)
    try:
        db.session.add(mbd)
        db.session.commit()
        med_unit = get_medicine_unit(medicine_unit_id=int(medicine_unit_id))
        if med_unit[0].quantity < int(quantity):
            return None
        else:
            med_unit[0].quantity -= int(quantity)
        return mbd
    except:
        return None

def create_bill(medical_bill_id):
    temp = get_medical_bill_value(medical_bill_id)
    bill = Bill(medical_bill_id=temp[0], value=temp[1])
    try:
        db.session.add(bill)
        db.session.commit()
        return bill
    except:
        return None

def get_bill(id=None):
    if id:
        temp = db.session.query(Bill.id, Bill.value, Patient.last_name, Patient.first_name, Patient.phone_number,\
                                Patient.date_of_birth, Medical_bill.create_date, Bill.pay)\
                                .join(Medical_bill, Medical_bill.id == Bill.medical_bill_id)\
                                .join(Patient, Patient.id == Medical_bill.patient_id)\
                                .filter(Bill.id.__eq__(int(id)))
        return temp.first()
    else:
        return None

def pay_bill(id=None):
    if id:
        try:
            Bill.query.filter_by(id=int(id)).update(dict(pay=True))
            db.session.commit()
            return True
        except:
            return False
    else:
        return False

def pay_bill_with_momo(bill_id, amount, re_url):

    # parameters send to MoMo get get payUrl
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = "MOMO"
    accessKey = "F8BBA842ECF85"
    secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"
    orderInfo = "Pay with MoMo"
    redirectUrl = re_url
    ipnUrl = "http://momo.vn"
    amount = str(amount)
    orderId = str(bill_id)
    requestId = str(uuid.uuid4())
    requestType = "captureWallet"
    extraData = ""  # pass empty value or Encode base64 JsonString

    # before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl&orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId&requestType=$requestType
    rawSignature = "accessKey=" + accessKey + "&amount=" + amount + "&extraData=" + extraData + "&ipnUrl=" + ipnUrl + "&orderId=" + orderId + "&orderInfo=" + orderInfo + "&partnerCode=" + partnerCode + "&redirectUrl=" + redirectUrl + "&requestId=" + requestId + "&requestType=" + requestType

    # signature
    h = hmac.new(bytes(secretKey, 'UTF-8'), rawSignature.encode(), hashlib.sha256)
    signature = h.hexdigest()
    data = {
        'partnerCode': partnerCode,
        'partnerName': "Test",
        'storeId': "MomoTestStore",
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': redirectUrl,
        'ipnUrl': ipnUrl,
        'lang': "vi",
        'extraData': extraData,
        'requestType': requestType,
        'signature': signature
    }
    data = json.dumps(data)
    data = bytes(data, encoding='utf-8')
    clen = len(data)
    req = urllib.request.Request(endpoint, data=data,\
                                 headers={'Content-Type': 'application/json',\
                                          'Content-Length': clen,'User-Agent': 'Mozilla/5.0'}, method='POST')
    try:
        f = urllib.request.urlopen(req)
        response = f.read()
        f.close()
        return json.loads(response)['payUrl']
    except Exception as e:
        print(e)
        return None

def get_cost():
    total = db.session.query(Other.cost).limit(1)
    return total.first()[0]

def get_limit_slot():
    total = db.session.query(Other.slot).limit(1)
    return total.first()[0]

def get_list_admin(user):
    dsqtv = []
    if user.is_authenticated:
        dsqtv = User.query.filter(User.user_role == UserRole.ADMIN, User.name != user.name).all()
    return dsqtv

def check_login(username , password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password)).first()

def check_role(user):
    if user.is_authenticated:
        if user.user_role == UserRole.ADMIN:
            return "Quản trị viên hệ thống"
        elif user.user_role == UserRole.NURSE:
            return "Y tá"
        return "Bác sĩ"

def check_sex(user):
    if user.is_authenticated:
        if user.sex == Sex.MALE:
            return "Nam"
        elif user.sex == Sex.FEMALE:
            return  "Nữ"
        return "Không muốn trả lời"


def check_login_of_current_user(password, user):
    if user.is_authenticated:
        if str(hashlib.md5(password.encode("utf-8")).hexdigest()).__eq__(user.password.strip()):
            return True
    return False


def check_info_for_change(user,avatar = None, name = None, username = None,day_of_birth = None,sex = None, phone = None, new_password = None, email = None):
     if user.is_authenticated:
        user_current = User.query.filter(User.username == user.username).first()
        if user_current:
            if username:
                user_current.username = username
                db.session.commit()
            if name:
                user_current.name = name
                db.session.commit()
            if avatar:
                user_current.avatar = avatar
                db.session.commit()
            if email:
                user_current.email = email
                db.session.commit()
            if day_of_birth:
                day_of_birth = str(day_of_birth)
                user_current.date_of_birth = datetime.datetime.strptime(day_of_birth,'%Y-%m-%d')
                db.session.commit()
            if phone:
                user_current.phone_number = str(phone)
                db.session.commit()
            if new_password:
                new_password = str(hashlib.md5(new_password.strip().encode('utf-8')).hexdigest())
                user_current.password = new_password
                db.session.commit()
            if sex:
                sex_enum = Sex.UNSPECIFIED
                if str(sex) == "1":
                    sex_enum = Sex.MALE
                if str(sex) == "2":
                    sex_enum = Sex.FEMALE
                user_current.sex = sex_enum
                db.session.commit()


def check_role_for_render(user):
    if user.is_authenticated:
        if user.user_role == UserRole.NURSE:
            return 'nurse_view'
        elif user.user_role == UserRole.DOCTOR:
            return 'doctor_view'

def check_unique_info(username,phone,email, user):
    kq = []
    if user.is_authenticated:
        if username:
            user_exist = User.query.filter(User.username == username.strip(), User.username != user.username).first()
            if user_exist:
                kq.append('username')
        if phone:
            user_exist = User.query.filter(User.phone_number == str(phone).strip(), User.phone_number != user.phone_number).first()
            if user_exist:
                kq.append('phone')
        if email:
            user_exist = User.query.filter(User.email == email.strip(), User.email != user.email).first()
            if user_exist:
                kq.append('email')
    return kq

account_sid = 'AC0c21ea651869130bbf4d2d34aa836370'
auth_token = '878946ca41cc1e75b70b2ab4e1f8fa9b'
def send_sms_to_patient(dayexam):
    client = Client(account_sid, auth_token)
    if dayexam:
        getday = db.session.query(Examination).get(dayexam)
    phone = get_patient_in_exam(str(getday.date))
    for idx,value in enumerate(phone):
        # print(value[5])
        try:
            message = client.messages.create(
                body='Lịch khám: '+str(getday.date),
                from_='+19166940519',
                to= '+84' + str(value[5])
            )
        except:
            continue
    return True

def check_phone_number_of_patient(phone_number):
    if phone_number:
        pt = Patient.query.filter(Patient.phone_number.__eq__(phone_number.strip())).first()
        return pt

def check_info_for_error_ms(current_user= None,avatar = None, name = None, username = None,day_of_birth = None,sex = None, phone = None, new_password = None, email = None, password = None, confirm = None):
    avatar_path = ''
    error_ms = ''
    try:
        if check_login_of_current_user(password, current_user):
            if (new_password != '' and confirm != '') or (new_password == '' and confirm == ''):
                if not new_password.strip().__eq__(confirm.strip()):
                    error_ms = 'Xác nhận mật khẩu mới không khớp !!!'
                else:
                    list = check_unique_info(username=username, phone=phone, email=email, user=current_user)
                    if len(list) == 0:
                        if avatar.filename.endswith('.png') or avatar.filename.endswith(
                                '.jpg') or avatar.filename.endswith('.jpeg') or not avatar:
                            if avatar:
                                res = cloudinary.uploader.upload(avatar)
                                avatar_path = res['secure_url']
                            try:
                                check_info_for_change(user=current_user, avatar=avatar_path, name=name,
                                                      username=username, day_of_birth=day_of_birth, email=email,
                                                      sex=sex, phone=phone, new_password=new_password)
                                error_ms = "Thay đổi thành công!!!"
                            except Exception as ex:
                                error_ms = str(ex)
                        else:
                            error_ms = 'File avatar không hợp lệ (*.jpeg/*.png/*.jpg)!!!'
                    else:
                        error_ms = 'Những thông tin sau đã tồn tại: '
                        for i in range(len(list)):
                            if i != 0:
                                error_ms += ', ' + list[i]
                            else:
                                error_ms += list[i]

            else:
                error_ms = 'Xác nhận mật khẩu mới không khớp !!!'

        else:
            error_ms = 'Nhập sai mật khẩu hiện tại !!!'
    except Exception as ex:
        error_ms = str(ex)
    return error_ms

def add_comment(patient_comment, content_comment, star_comment):
    c = Comment(patient_comment = patient_comment, content_comment=content_comment,star_comment=star_comment)

    db.session.add(c)
    db.session.commit()

    return c

def get_comment():

    return db.session.query(Comment.patient_comment,Comment.content_comment,Comment.star_comment).order_by(Comment.id.desc()).all()

def medical_register(phone_number, first_name, last_name, sex, date_of_birth, date_of_exam):
    if not last_name.strip():
        return jsonify({'code': 400,
                        'error_ms': 'Bạn không được để trống họ!!!'})
    if not first_name.strip():
        return jsonify({'code': 400,
                        'error_ms': 'Bạn không được để trống tên!!!'})
    if not date_of_birth:
        return jsonify({'code': 400,
                        'error_ms': 'Bạn không được để trống ngày sinh!!!'})
    if not date_of_exam:
        return jsonify({'code': 400,
                        'error_ms': 'Bạn không được để trống ngày đăng ký khám bệnh!!!'})
    patient = check_phone_number_of_patient(phone_number=phone_number)
    try:
        slot = get_limit_slot()
        list_patient = get_patient_in_exam(exam_date=date_of_exam)
        if list_patient and list_patient[0][8]:
            return jsonify({'code': 400,
                            'error_ms': 'Bạn không thể đăng ký khám bệnh ngày này!!!'})
        if not patient:
            if not list_patient or len(list_patient) < slot:
                term_patient = create_patient(last_name=last_name, first_name=first_name, sex=sex, phone_number=phone_number,\
                               date_of_birth=date_of_birth)
                register_into_examination(patient_id=term_patient.id, exam_date=date_of_exam)
            else:
                return jsonify({'code': 400,
                                'error_ms': 'Đã hết suất khám, vui lòng chọn ngày khác!!!'})
        else:
            if not list_patient or len(list_patient) < slot:
                if list_patient:
                    if check_patient_in_an_exam(patient, list_patient):
                        return jsonify({'code': 400,
                                    'error_ms': 'Bạn đã đăng ký lịch khám vào ngày này rồi!!!'})
                register_into_examination(patient_id=patient.id, exam_date=date_of_exam)
            else:
                return jsonify({'code': 400,
                                'error_ms': 'Đã hết suất khám, vui lòng chọn ngày khác!!!'})
    except Exception as ex:
        return jsonify({'code': 400,
                        'error_ms': str(ex)})
    return  jsonify({'code': 200,
                     'error_ms': 'Đăng ký thành công!!!'})
