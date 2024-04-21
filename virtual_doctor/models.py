#!/usr/bin/python3
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# customer table
class Customers(Base):
    __tablename__ = 'customers'
    cust_id = Column(String, unique=True, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone_no = Column(String, unique=True)
    password = Column(String)
    history =  relationship('History', backref='customer')

    def __repr__(self):
        #return a string representation of the table
        return f'Customers(cust_id={self.cust_id}, \
        first_name={self.first_name}, \
        last_name={self.last_name},\
        email={self.email}, \
        phone_no={self.phone_no}, \
        password={self.password})'

#table to store the booking records of customers
class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    cust_id = Column(String, ForeignKey('customers.cust_id'))
    date = Column(String) #booking date
    service = Column(String)
    time = Column(String) #booking time
    cur_date = Column(DATETIME)
    doctor = Column(String)
    address = Column(String)

    def __repr__(self):
        #get a string representation of db objects
        return f'History(cust_id={self.cust_id},\
            id={self.id},\
                time={self.time},\
                    date={self.date},\
                    doctor={self.doctor},\
                    address={self.address},\
                        service={self.service},\
                        update_time={self.cur_date})'

#booking history done outside the client portal
class History_pub(Base):
    __tablename__ = 'history_pub'
    id = Column(Integer, primary_key=True)
    contact = Column(String)
    date = Column(String) #booking date
    service = Column(String)
    patient = Column(String)
    email = Column(String)
    time = Column(String) #booking time
    cur_date = Column(DATETIME)
    doctor = Column(String)
    address = Column(String)

    def __repr__(self):
        #get a string representation of db objects
        return f'History_pub(id={self.id},\
            contact={self.contact},\
                time={self.time},\
                    date={self.date},\
                    email={self.email}, \
                    doctor={self.doctor},\
                    address={self.address},\
                        service={self.service},\
                        update_time={self.cur_date},\
                            patient={self.patient})'

#table to store the feedback
class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    feedback = Column(String)
    name = Column(String)
    email = Column(String)

    def __repr__(self):
        #get a string representation of the table
        return f'Feedback(id = {self.id}, \
                 message = {self.feedback}, \
                 name = {self.name}, \
                 email = {self.email})'

