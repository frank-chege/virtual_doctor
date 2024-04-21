#!/usr/bin/python3
#creating a flask app and mapping api endpoints to 
#communicate with the database

from flask import Flask, request, redirect, url_for, flash, jsonify, render_template, session as flask_session
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from sqlalchemy import *
from sqlalchemy.orm import *
import random
import string
import os
import secrets
from flask_mail import Mail, Message
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.exc import *

#create a flask app
app = Flask(__name__)
app.secret_key = os.getenv('APP_KEY')

#create an engine
engine = create_engine('sqlite:///naismart.db')
#create the tables defined by the classes
Base.metadata.create_all(engine)

#create a session
Session = sessionmaker(bind=engine)
session = Session()

#load credentials stored in env
load_dotenv()

#configure my mail server
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

#home page
@app.route('/', methods=['GET'])
def home():
    '''returns the public homepage'''
    return render_template('/public/index.html')

#services page
@app.route('/services', methods=['GET'])
def services():
    '''returns the services page'''
    return render_template('/public/services.html')

#staff page
@app.route('/staff', methods=['GET'])
def staff():
    '''returns the staff page'''
    return render_template('/public/staff.html')

#forums page
@app.route('/forums', methods=['GET'])
def forums():
    '''returns the forums page'''
    return render_template('/public/forums.html')

#gallery page
@app.route('/gallery', methods=['GET'])
def gallery():
    '''returns the gallery page'''
    return render_template('/public/gallery.html')

#about page
@app.route('/about', methods=['GET'])
def about():
    '''returns the about page'''
    return render_template('/public/about.html')

#contact page
@app.route('/contact', methods=['GET'])
def contact():
    '''returns the contact page'''
    return render_template('/public/contact.html')

#help page
@app.route('/help', methods=['GET'])
def help():
    '''returns the help page'''
    return render_template('/public/help.html')


def gen_cust_id(length=10):
    '''generates a random customer id'''
    cust_id = string.ascii_letters + string.digits
    return ''.join(random.choice(cust_id) for x in range(length))

#registration endpoint
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #collects the user registration details and save the to the db
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone_no = request.form['phone_no']
        password = request.form['password']
        #hash the password
        hashed_pwd = generate_password_hash(password)
        #create a new customer
        newcust = Customers(
            first_name = first_name,\
            last_name = last_name,\
            email = email,\
            phone_no = phone_no,\
            password = hashed_pwd,\
            cust_id = gen_cust_id()
        )

        try:
            session.add(newcust)
            session.commit()
            #send an email to the user confirming registration
            msg = Message('HOSPITAL X REGISTRATION', sender='naismart@franksolutions.tech', recipients=[email])
            msg.body = 'Thank You for registering with HOSPITAL X!'
            mail.send(msg)
            '''
            #send an email to the admin informing of a new user
            users = session.query(Customers).filter_by(email=email).first()
            msg = Message('New user', sender='naismart@franksolutions.tech', recipients=['francischege602@gmail.com'])
            msg.body = f'{users.first_name} {users.last_name}\n\n\n'
            mail.send(msg)
            '''
            print('Email sent successfully!')
            flash('Registration was successful')
            return render_template('/public/sign_in.html')
        #errors arising due to unique constraint violation
        except IntegrityError:
            session.rollback
            flash('Number or email already exists!')
            return render_template('/public/sign_in.html')
        #other errors
        except:
            session.rollback()
            flash('An error occured. Please try again!')
            return render_template('/public/sign_up.html')
        finally:
            session.close()
    else:
        return render_template('/public/sign_up.html')

#sign_in endpoint
@app.route('/sign_in', methods=['POST', 'GET'])
def sign_in():
    """checks if the enterd password matches the one 
    stored in the database for the customer
    """
    if request.method == 'POST':
        ent_email = request.form['email']
        ent_pwd = request.form['password']
        #query the user based on the email
        user = session.query(Customers).filter_by(email=ent_email).first()
        #compare if the entered passwd matches the one in the database for that user
        if user and check_password_hash(user.password, ent_pwd):
            user = session.query(Customers).filter_by(email=ent_email).first()
            #create a session for the user
            if user:
                flask_session['name'] = user.first_name
                flask_session['cust_id'] = user.cust_id
            return render_template('/private/priv_index.html', name=flask_session.get('name'))
        else:
            #Alert the user of wrong credentials
            flash('Invalid password or email.Try again!')
            return redirect(url_for('sign_in'))
    else:
        #if method is GET
        return render_template('/public/sign_in.html')

#password reset
@app.route('/pwd_reset', methods=['POST', 'GET'])
def pwd_reset():
    if request.method == 'GET':
        return render_template('/public/pwd_reset.html')
    else:
        #POST. check if the email exists
        email = request.form['email']
        check_mail = session.query(Customers.email).filter_by(email=email).first()
        #mail exists
        if check_mail:
            #store the code in the user's session
            code = random.randint(111111, 999999)
            flask_session['code'] = code
            flask_session['email'] = email
            msg = Message('HOSPITAL X RESET PASSWORD', sender='naismart@franksolutions.tech',\
                                                    recipients=[email])
            msg.body = f'Use this code to reset your password\n\n {code}'
            mail.send(msg)
            flash('Enter the code to reset your password')
            return render_template('/public/new_pwd.html')
        #mail does not exist
        else:
            flash('The email does not exist!')
            return redirect(url_for('pwd_reset'))

#create a new password
@app.route('/new_pwd', methods=['POST'])
def new_pwd():
    #verify the code
    if flask_session.get('code') == int(request.form['code']):
        #update password
        password = request.form['new_pwd']
        #hash password
        hashed_pwd = generate_password_hash(password)
        user = session.query(Customers).filter_by(email=flask_session.get('email')).first()
        user.password = hashed_pwd
        #commit the changes
        session.commit()
        session.close()
        flash('Your password has been updated')
        
        #clear the code from the session
        flask_session.pop('code', None)
        return render_template('/public/sign_in.html')
    else:
        flash('Wrong code! Please try again!')
        return render_template('/public/new_pwd.html')

#private home page for looged in users
@app.route('/priv_home', methods=['GET'])
def priv_home():
    #checks if a user  has an active session and returns the logged in home page
    if 'cust_id' in flask_session:
        return render_template('/private/priv_index.html', name=flask_session.get('name'))
    else:
        #send the user to the login page
        return render_template('/public/index.html')

#booking page
@app.route('/book_now', methods=['GET', 'POST'])
def book_now():
    #check if user has an active session and generates a ticket
    if 'cust_id' in flask_session:
        #get data from the form
        if request.method == 'POST':
            #patient = request.form['patient']
            #contact = request.form['contact']
            service = request.form['service']
            date = request.form['date']
            time = request.form['time']
            #random name and address
            doctor = 'Doc. James'
            address = '130-0098 Ngong, Kajiado'
            #query the databse using cust_id to get user email
            user = session.query(Customers).filter_by(cust_id=flask_session['cust_id']).first()
            #create ticket
            #ticket = random.randint(1, 1000000)
            msg = Message('HOSPITAL X APPOINTMENT', sender='naismart@franksolutions.tech', recipients=[user.email])
            msg.body = f'Hello {user.first_name}, your appointment has been processed as follows:\n\n\
                        Service booked: {service}\n\
                        Date:           {date}\n\
                        Time:           {time}\n\
                        Doctor:         {doctor}\n\
                        Address:        {address}'
            mail.send(msg)
            flash('You have successfully booked. Please check your email for more details')
            #store the details in the history database
            #get the current time and date to order the database
            cur_date = datetime.now()
            new_record = History(
                cust_id = flask_session.get('cust_id'),
                #patient = patient,
                #contact = contact,
                service = service,
                date = date,
                time = time,
                doctor = doctor,
                address = address,
                cur_date = cur_date
            )
            try:
                session.add(new_record)
                session.commit()
                session.close()
            except:
                session.rollback()
            finally:
                return render_template('/private/priv_index.html', name=flask_session.get('name'))
        else:
            #get method
            return render_template('/private/priv_book.html', name=flask_session.get('name'))
    else:
        #user is not signed in
        #get data from the form
        if request.method == 'POST':
            patient = request.form['patient']
            contact = request.form['contact']
            email = request.form['email']
            service = request.form['service']
            date = request.form['date']
            time = request.form['time']
            #random name and address
            doctor = 'Doc. James'
            address = '130-0098 Ngong, Kajiado'
            msg = Message('HOSPITAL X APPOINTMENT', sender='naismart@franksolutions.tech', recipients=[email])
            msg.body = f'Hello {patient}, your appointment has been processed as follows:\n\n\
                        Service booked: {service}\n\
                        Date:           {date}\n\
                        Time:           {time}\n\
                        Doctor:         {doctor}\n\
                        Address:        {address}'
            mail.send(msg)
            flash('You have successfully booked. Please check your email for more details')
            #get the current date and time
            cur_date = datetime.now()
            #check if email is already registered to save data to private history table
            user = session.query(Customers).filter_by(email=email).first()
            #email is registered
            if user:
                new_record = History(
                cust_id = user.cust_id,
                service = service,
                date = date,
                time = time,
                doctor = doctor,
                address = address,
                cur_date = cur_date
                )
                try:
                    session.add(new_record)
                    session.commit()
                    session.close()
                except:
                    session.rollback()
                finally:
                    return render_template('/public/index.html')
            #email is not registered
            else:
                #store the details in the public history database
                new_record = History_pub(
                    patient = patient,
                    contact = contact,
                    email = email,
                    service = service,
                    date = date,
                    time = time,
                    doctor = doctor,
                    address = address,
                    cur_date = cur_date
                    )
                try:
                    session.add(new_record)
                    session.commit()
                    session.close()
                except:
                    session.rollback()
                finally:
                    return render_template('/public/index.html')
        else:
            #get method
            return render_template('/public/pub_book.html')

#history endpoint
@app.route('/history', methods=['GET'])
def history():
    if 'cust_id' in flask_session:
        #retrieve the booking records of a customer
        #retrieve the records in descending order
        hist = session.query(History).order_by(History.cur_date.desc()).filter_by(cust_id=flask_session.get('cust_id')).all()
        #flash('You have not made any bookings yet')
        return render_template('/private/priv_history.html', hist=hist)

#virtual doctor endpoint
@app.route('/virtual', methods=['GET'])
def virtual():
    if 'cust_id' in flask_session:
        '''access virtual doctor platform'''
        return render_template('/private/virtual.html')

#payments endpoint
@app.route('/pay', methods=['GET'])
def pay():
    if 'cust_id' in flask_session:
        '''access payments platform'''
        return render_template('/private/pay.html')

#pharmacy endpoint
@app.route('/pharmacy', methods=['GET'])
def pharmacy():
    if 'cust_id' in flask_session:
        '''access pharmacy platform'''
        return render_template('/private/pharmacy.html')

#feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    #retrieve user feedback and send confirmation email
    feedback = request.form['feedback']
    name = request.form['name']
    email = request.form['email']
    new_record = Feedback(
        feedback = feedback,
        name = name,
        email = email
    )
    try:
        session.add(new_record)
        session.commit()
        #send confirmation email
        msg = Message('HOSPITAL X FEEDBACK', sender='naismart@franksolutions.tech', recipients=[email])
        msg.body = f'Hello {name}, thank you for your feedback.\nWe will reach out to you soon with a response.If you have any other issues feel free to reach out to us. Nice time!'
        mail.send(msg)
        #send feedback to the admin
        msg = Message('HOSPITAL CUSTOMER FEEDBACK', sender='naismart@franksolutions.tech', recipients=['francischege602@gmail.com'])
        msg.body = f'Client\'s name: {name}\nMessage: {feedback}'
        mail.send(msg)
        flash('Your feedback was successfully submitted')
        return render_template('/public/index.html')
    except:
        session.rollback()
        flash('An error occured! Your feedback was not submitted! Try again!')
        return render_template('/public/contact.html')
    finally:
        session.close()

#sign out endpoint
@app.route('/sign_out', methods=['GET'])
def sign_out():
    #logs out the user
    flask_session.pop('cust_id', None)
    return render_template('/public/index.html')

#run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)