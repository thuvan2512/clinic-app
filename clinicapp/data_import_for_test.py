from clinicapp import db, utils, models
from datetime import datetime, date

if __name__ == '__main__':
    u1 = models.User(name="Thu", username="thu123", user_role=models.UserRole.ADMIN,\
                     sex=models.Sex.MALE, date_of_birth=datetime.now(), phone_number='0877158491', email='ABC')
    u2 = models.User(name="Hieu", username="hieu123", user_role=models.UserRole.ADMIN,\
                     sex=models.Sex.MALE, date_of_birth=datetime.now(), phone_number='0944540746', email='XYZ')
    u3 = models.User(name="Huy", username="huy123", user_role=models.UserRole.ADMIN,\
                     sex=models.Sex.MALE, date_of_birth=datetime.now(), phone_number='0937461321', email='423')
    u4 = models.User(name="Huynh", username="huynh123", user_role=models.UserRole.ADMIN,\
                     sex=models.Sex.MALE, date_of_birth=datetime.now(), phone_number='0989915415', email='A756C')
    u5 = models.User(name="USER1", username="user1", user_role=models.UserRole.NURSE, \
                     sex=models.Sex.MALE, date_of_birth=datetime.now(), phone_number='131268762', email='A41C')
    users = [u1, u2, u3, u4, u5]
    for u in users:
        db.session.add(u)
    db.session.commit()

    p1 = models.Patient(first_name="Thu", last_name="Nguyen Van", sex=models.Sex.MALE,\
                        date_of_birth=datetime.now(), phone_number='0784301745')
    p2 = models.Patient(first_name="Hieu", last_name="Nguyen Ngoc", sex=models.Sex.MALE,\
                        date_of_birth=datetime.now(), phone_number='0944540746')
    p3 = models.Patient(first_name="Huy", last_name="Nguyen Dinh", sex=models.Sex.MALE,\
                        date_of_birth=datetime.now(), phone_number='0937461321')
    p4 = models.Patient(first_name="Huynh", last_name="Tran Le", sex=models.Sex.MALE,\
                        date_of_birth=datetime.now(), phone_number='0989915415')
    pa = [p1, p2, p3, p4]
    for p in pa:
        db.session.add(p)
    db.session.commit()

    e1 = models.Examination(user_id=1, date=datetime(2021, 12, 31))
    e1.patients.append(p1)
    e2 = models.Examination(user_id=2, date=datetime(2022, 1, 1))
    e2.patients.append(p2)
    e3 = models.Examination(user_id=3, date=datetime(2021, 1, 2))
    e3.patients.append(p3)
    e4 = models.Examination(user_id=4, date=datetime.now())
    e4.patients.append(p4)
    exam = [e1, e2, e3, e4]
    for e in exam:
        db.session.add(e)
    db.session.commit()

    mb1 = models.Medical_bill(user_id=1, diagnosis="abc", symptom="xyz", patient_id=1)
    mb2 = models.Medical_bill(user_id=2, diagnosis="abc", symptom="xyz", \
                              create_date=datetime(2021, 12, 16), patient_id=2)
    mb3 = models.Medical_bill(user_id=3, diagnosis="abc", symptom="xyz",\
                              create_date=datetime(2021, 12, 15), patient_id=3)
    mb4 = models.Medical_bill(user_id=4, diagnosis="abc", symptom="xyz", patient_id=4)
    mb5 = models.Medical_bill(user_id=3, diagnosis="abc", symptom="xyz",\
                              create_date=datetime(2021, 12, 15), patient_id=1)
    mb6 = models.Medical_bill(user_id=4, diagnosis="abc", symptom="xyz",\
                              create_date=datetime(2021, 5, 20), patient_id=2)
    mb7 = models.Medical_bill(user_id=2, diagnosis="abc", symptom="xyz",\
                              create_date=datetime(2021, 5, 19), patient_id=3)
    mb8 = models.Medical_bill(user_id=4, diagnosis="abc", symptom="xyz",\
                              create_date=datetime(2021, 5, 17), patient_id=4)
    mbs = [mb1, mb2, mb3, mb4, mb5, mb6, mb7, mb8]
    for mb in mbs:
        db.session.add(mb)
    db.session.commit()

    md1 = models.Medicine(name="acepron")
    md2 = models.Medicine(name="allerphast")
    md3 = models.Medicine(name="allvitamine")
    md4 = models.Medicine(name="avarino")
    mds = [md1, md2, md3, md4]
    for md in mds:
        db.session.add(md)
    db.session.commit()

    unt1 = models.Unit_tag(name='ống')
    unt2 = models.Unit_tag(name='vỉ')
    unt3 = models.Unit_tag(name='hộp')
    unts = [unt1, unt2, unt3]
    for unt in unts:
        db.session.add(unt)
    db.session.commit()

    mdu1 = models.Medicine_unit(unit_id=1, price=50000, quantity=50, medicine_id=1)
    mdu2 = models.Medicine_unit(unit_id=2, price=30000, quantity=50, medicine_id=1)
    mdu3 = models.Medicine_unit(unit_id=3, price=70000, quantity=50, medicine_id=2)
    mdu4 = models.Medicine_unit(unit_id=3, price=200000, quantity=50, medicine_id=2)
    mdu5 = models.Medicine_unit(unit_id=2, price=80000, quantity=50, medicine_id=3)
    mdu6 = models.Medicine_unit(unit_id=1, price=30000, quantity=50, medicine_id=3)
    mdu7 = models.Medicine_unit(unit_id=2, price=80000, quantity=50, medicine_id=4)
    mdu8 = models.Medicine_unit(unit_id=1, price=30000, quantity=50, medicine_id=3)
    mdus = [mdu1, mdu2, mdu3, mdu4, mdu5, mdu6, mdu7, mdu8]
    for mdu in mdus:
        db.session.add(mdu)
    db.session.commit()

    mbd1 = models.Medical_bill_detail(medical_bill_id=1,  medicine_unit_id=1, quantity=2)
    mbd2 = models.Medical_bill_detail(medical_bill_id=1, medicine_unit_id=2, quantity=1)
    mbd3 = models.Medical_bill_detail(medical_bill_id=2, medicine_unit_id=4, quantity=3)
    mbd4 = models.Medical_bill_detail(medical_bill_id=2, medicine_unit_id=6, quantity=10)
    mbd5 = models.Medical_bill_detail(medical_bill_id=2, medicine_unit_id=2, quantity=5)
    mbd6 = models.Medical_bill_detail(medical_bill_id=3, medicine_unit_id=3, quantity=8)
    mbd7 = models.Medical_bill_detail(medical_bill_id=3, medicine_unit_id=6, quantity=3)
    mbd8 = models.Medical_bill_detail(medical_bill_id=4, medicine_unit_id=5, quantity=9)
    mbd9 = models.Medical_bill_detail(medical_bill_id=4, medicine_unit_id=7, quantity=3)
    mbd10 = models.Medical_bill_detail(medical_bill_id=4, medicine_unit_id=8, quantity=15)
    mbd11 = models.Medical_bill_detail(medical_bill_id=5, medicine_unit_id=1, quantity=5)
    mbd12 = models.Medical_bill_detail(medical_bill_id=5, medicine_unit_id=4, quantity=7)
    mbd13 = models.Medical_bill_detail(medical_bill_id=6, medicine_unit_id=2, quantity=1)
    mbd14 = models.Medical_bill_detail(medical_bill_id=6, medicine_unit_id=3, quantity=4)
    mbd15 = models.Medical_bill_detail(medical_bill_id=7, medicine_unit_id=7, quantity=6)
    mbd16 = models.Medical_bill_detail(medical_bill_id=7, medicine_unit_id=4, quantity=3)
    mbd17 = models.Medical_bill_detail(medical_bill_id=8, medicine_unit_id=5, quantity=9)
    mbd18 = models.Medical_bill_detail(medical_bill_id=8, medicine_unit_id=8, quantity=3)
    mbds = [mbd1, mbd2, mbd3, mbd4, mbd5, mbd6, mbd7, mbd8, mbd9, mbd10, mbd11, mbd12, mbd13, mbd14, mbd15, mbd16, mbd17, mbd18]
    for mbd in mbds:
        db.session.add(mbd)
    db.session.commit()

    other = models.Other()
    db.session.add(other)
    db.session.commit()
    temp = utils.get_cost()
    bills = utils.get_medical_bill_value()
    for b in bills:
        bill = models.Bill(medical_bill_id=b[0], value=b[1] + temp)
        db.session.add(bill)
    db.session.commit()

    db.create_all()
