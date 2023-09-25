from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, render_template_string
from .models import User, CRM, Organization, db
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Organization
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import smtplib
from email.mime.text import MIMEText
import datetime
from email.mime.multipart import MIMEMultipart


auth = Blueprint('auth', __name__)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except (SignatureExpired, BadTimeSignature):
        return False
    return email

def send_verification_email(email, token, firstname):
    # Generate verification URL
    verification_url = url_for('confirm_email', token=token, _external=True)
    print(f"Generated verification URL: {verification_url}")

    # Debug print
    print(f"Debug - verification_url: {verification_url}")

    # Load email content from template
    email_content = render_template('email_verification.html', verification_url=verification_url, firstname=firstname)
    print(f"Generated email content: {email_content}")  # Debug print
    # Debug print
    print(f"Debug - email_content: {email_content}")

    # Setup MIME Multipart object
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Confirm Your Email Address"
    msg['From'] = "goaliebrady00@gmail.com"
    msg['To'] = email

    # Attach MIMEText object for HTML content
    part = MIMEText(email_content, 'html')
    msg.attach(part)

    # Send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('goaliebrady00@gmail.com', 'cmvu lgly jwqa lkre')  # Consider using environment variables for these.
    server.sendmail('goaliebrady00@gmail.com', [email], msg.as_string())
    server.quit()

@auth.route('/confirm/<token>', methods=['GET'])
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        flash('Invalid or expired token', 'danger')
        return render_template('email_verification_failure.html', user=current_user)

    user = User.query.filter_by(email=email).first()
    if user.email_confirmed and user.email_confirmed_on:
        flash('Email already verified', 'success')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.datetime.utcnow()  # Or any other value that you want to set
        db.session.commit()
        flash('Email verified', 'success')

    return render_template('email_verification_success.html', user=current_user)

def send_email(subject, recipients, html_body):
    msg = MIMEText(html_body, 'html')
    msg['Subject'] = subject
    msg['From'] = 'goaliebrady00@gmail.com'
    msg['To'] = ', '.join(recipients)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('goaliebrady00@gmail.com', 'cmvu lgly jwqa lkre')
    server.sendmail('goaliebrady00@gmail.com', recipients, msg.as_string())
    server.quit()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if not user.email_confirmed:
                flash('Please confirm your email address.', category='error')
                return render_template('login.html', user=current_user)
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
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
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
        elif len(email) < 2:
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
            flash('Phone number must be greater than 9 characters.', category='error')
        elif len(password) < 8:
            flash('Password must be greater than 7 characters.', category='error')
        else:
            new_organization = Organization(name=company)
            db.session.add(new_organization)
            db.session.commit()

            new_user = User(
                email=email, 
                firstname=firstname, 
                lastname=lastname, 
                phonenumber=phonenumber, 
                password=generate_password_hash(password, method="sha256"), 
                company=company,
                is_admin=True,
                organization_id=new_organization.id
            )
            db.session.add(new_user)
            db.session.commit()

            # Generate token
            token = generate_confirmation_token(new_user.email)
            
            # Create email content
            subject = "Please confirm your email"
            verification_url = url_for('auth.confirm_email', token=token, _external=True)
            html = render_template('email_verification.html', verification_url=verification_url, user=current_user, firstname=firstname)
            
            # Send email
            msg = MIMEText(html, 'html')
            msg['Subject'] = subject
            msg['From'] = 'goaliebrady00@gmail.com'
            msg['To'] = new_user.email
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('goaliebrady00@gmail.com', 'cmvu lgly jwqa lkre')
            server.sendmail('goaliebrady00@gmail.com', [new_user.email], msg.as_string())
            server.quit()
            
            flash('A confirmation email has been sent via email. Please confirm to continue.', 'success')
            return render_template('login.html', user=current_user)

    return render_template('sign-up.html', user=current_user)

# ... (other imports and configurations)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = generate_confirmation_token(email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            html = render_template('reset_password_email.html', reset_url=reset_url, user=current_user)
            send_email('Reset Your Password', [user.email], html)
            flash('A password reset email has been sent.', 'success')
        else:
            flash('Email does not exist.', 'error')
    return render_template('forgot_password.html', user=current_user)

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password == confirm_password:
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(new_password, method='sha256')
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Passwords do not match.', 'error')
    return render_template('reset_password.html', user=current_user)
