from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'), user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method =='POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phonenumber = request.form.get('phonenumber')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        company = request.form.get('company')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists!', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstname) < 2:
            flash('First name must be greater than 1 characters.', category='error')
        elif password != password2:
            flash('Your passwords do not match.', category='error')
        elif len(company) < 1:
            flash('Company name cannot be empty.', category='error')
        elif len(lastname) < 2:
            flash('Last name must be greater than 1 characters.', category='error')
        elif len(phonenumber) < 10:
            flash('phone number must be greater than 9 characters.', category='error')
        elif len(password) < 8:
            flash('Password must be greater than 7 characters.', category='error')
        else:
            # add user to database
            new_user = User(email=email, firstname=firstname, lastname=lastname, phonenumber=phonenumber, password=generate_password_hash(password, method="sha256"), company=company)
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='success')
            login_user(user, remember=True)
            return redirect(url_for('views.home'), user=current_user)

    return render_template('sign-up.html', user=current_user)
