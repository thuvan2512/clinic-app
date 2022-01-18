from sqlalchemy import Column, Integer, String, Enum, Float, Boolean, Date, ForeignKey, Text, Table
from sqlalchemy.orm import relationship, backref
from clinicapp import db, utils
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin, current_user
import hashlib

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    NURSE = 2
    DOCTOR = 3

class Sex(UserEnum):
    MALE = 1
    FEMALE = 2
    UNSPECIFIED = 3

class User(BaseModel, UserMixin):
    __tablename__='user'
    __table_args__ = {'extend_existing': True}
    name = Column(String(100), nullable=False)
    username = Column(String(20), nullable=False, unique=True)
    password = Column(String(255), nullable=False, default=str(hashlib.md5(str(1).encode("utf-8")).hexdigest()))
    date_of_birth = Column(Date, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    avatar = Column(String(100), default='')
    phone_number = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    joined_date = Column(Date, default=datetime.now())
    user_role = Column(Enum(UserRole), nullable=False)
    medical_bills = relationship('Medical_bill', backref='user', lazy=True)
    examinations = relationship('Examination', backref='user', lazy=True)

    def __str__(self):
        return self.name

class Other(BaseModel):
    __tablename__ = 'other'
    __table_args__ = {'extend_existing': True}
    cost = Column(Float, default=100000.0, nullable=False)
    slot = Column(Integer, default=30, nullable=False)
    active = Column(Boolean, default=True)

Exam_patient = db.Table('exam_patient',\
                        Column('exam_id', Integer, ForeignKey('examination.id'), primary_key=True),\
                        Column('patient_id', Integer, ForeignKey('patient.id'), primary_key=True),\
                        extend_existing=True)

class Examination(BaseModel):
    __tablename__ = 'examination'
    __table_args__ = {'extend_existing': True}
    date = Column(Date, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    apply = Column(Boolean, default=False)
    patients = relationship('Patient', secondary=Exam_patient, lazy='subquery',\
                            backref=backref('examinations', lazy=True))

class Patient(BaseModel):
    __tablename__ = 'patient'
    __table_args__ = {'extend_existing': True}
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(Enum(Sex), nullable=False)
    phone_number = Column(String(50), nullable=False, unique=True)
    medical_bills = relationship('Medical_bill', backref='patient', lazy=True)

class Medical_bill(BaseModel):
    __tablename__ = 'medical_bill'
    __table_args__ = {'extend_existing': True}
    create_date = Column(Date, default=datetime.now())
    diagnosis = Column(Text)
    symptom = Column(Text)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    medical_bill_detail = relationship('Medical_bill_detail', backref='medical_bill', lazy=True)
    bill = relationship('Bill', backref='medical_bill', lazy=True)
    patient_id = Column(Integer, ForeignKey(Patient.id), nullable=False)


class Bill(BaseModel):
    __tablename__ = 'bill'
    __table_args__ = {'extend_existing': True}
    value = Column(Float, default=0)
    medical_bill_id = Column(Integer, ForeignKey(Medical_bill.id), nullable=False)
    pay = Column(Boolean, default=False)


class Medicine(BaseModel):
    __tablename__ = 'medicine'
    __table_args__ = {'extend_existing': True}
    name = Column(String(255), nullable=False)
    effect = Column(Text)
    medicine_units = relationship('Medicine_unit', backref='medicine', lazy=True)

    def __str__(self):
        return self.name


class Unit_tag(BaseModel):
    __tablename__ = 'unit_tag'
    __table_args__ = {'extend_existing': True}
    name = Column(String(50), nullable=False, unique=True)
    medicine_units = relationship('Medicine_unit', backref='unit_tag', lazy=True)

    def __str__(self):
        return self.name

class Medicine_unit(BaseModel):
    __tablename__ = 'medicine_unit'
    __table_args__ = {'extend_existing': True}
    unit_id = Column(Integer, ForeignKey(Unit_tag.id), nullable=False)
    price = Column(Float, default=0)
    quantity = Column(Integer, nullable=False, default=0)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=False)
    medical_bill_details = relationship('Medical_bill_detail', backref='medicine_unit', lazy=True)

    def __str__(self):
        return str(self.medicine) + "-" + str(self.unit_tag)

class Medical_bill_detail(db.Model):
    __tablename__ = 'medicine_bill_detail'
    __table_args__ = {'extend_existing': True}
    medical_bill_id = Column(Integer, ForeignKey(Medical_bill.id), nullable=False, primary_key=True)
    medicine_unit_id = Column(Integer, ForeignKey(Medicine_unit.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    use = Column(Text)

    def __str__(self):
        return "id:" + str(self.medical_bill_id) + "-" + self.medicine_unit.medicine + "-" + self.medicine_unit.unit_tag

class Comment(BaseModel):
    __tablename__ = 'comment'
    __table_args__ = {'extend_existing': True}
    patient_comment = Column(String(50))
    content_comment = Column(String(180))
    star_comment = Column(Integer)

    def __str__(self):
        return self.name;

if __name__ == '__main__':
    db.create_all()