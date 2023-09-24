# let's import the flask
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os # importing operating system module
import os
from my_package.__init__ import create_app
from flask_login import LoginManager
from flask_login import current_user,login_required
from my_package.models import CRM, User, db, Note, Tags, Organization
from flask import send_from_directory
import csv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc, asc
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from datetime import datetime
from math import ceil
import smtplib
from email.mime.text import MIMEText


app = Flask(__name__)

app = create_app()
# to stop caching static file

from my_package.models import *

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


app.secret_key = '823r9h2983hrf23j89fj29r8329'

from my_package.auth import auth
from my_package.views import views 


@app.route('/') # this decorator create the home route
def home ():
    techs = ['HTML', 'CSS', 'Flask', 'Python']
    name = '30 Days Of Python Programming'
    return render_template('home.html', techs=techs, name = name, title = 'Home', user=current_user)

@app.route('/upcoming_due_dates', methods=['GET'])
@login_required
def upcoming_due_dates():
    current_time = datetime.utcnow()
    
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    # Query to join CRM and Note, filter by organization_id and due date.
    query = (db.session.query(CRM, Note)
             .join(Note, Note.contact_id == CRM.id)
             .filter(Note.due_date > current_time)
             .filter(CRM.organization_id == current_user.organization_id)
             .order_by(Note.due_date.asc()))

    # Pagination
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_items = query.count()
    total_pages = ceil(total_items / per_page)  # Calculate total pages

    # Create a list of pages for pagination
    pages = list(range(1, total_pages + 1))

    # Additional code for pagination links
    next_url = url_for('upcoming_due_dates', page=page + 1) if page < total_pages else None
    prev_url = url_for('upcoming_due_dates', page=page - 1) if page > 1 else None

    return render_template('upcoming_due_dates.html', 
                           contacts_with_due_dates=items, 
                           next_url=next_url, 
                           prev_url=prev_url, 
                           total_pages=total_pages,
                           current_page=page,
                           pages=pages,
                           user=current_user)


s = URLSafeTimedSerializer(app.secret_key)

def send_email(subject, recipient, body):
    sender = 'goaliebrady00@gmail.com'
    password = 'cmvu lgly jwqa lkre'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

@app.route('/invite_user', methods=['GET', 'POST'])
def invite_user():
    if request.method == 'POST':
        email = request.form['email']

        # Generate a secure token
        data = {'email': email, 'organization_id': current_user.organization_id}
        token = s.dumps(data, salt='email-invite')

        # Generate the URL for email
        invitation_link = url_for('accept_invite', token=token, _external=True)

        subject = "You're Invited to Join Our Organization"
        body = f'You have been invited to join our organization. Click the link to accept: {invitation_link}'

        if send_email(subject, email, body):
            flash('Invitation sent successfully.', 'success')
        else:
            flash('An error occurred while sending the invitation.', 'danger')

        return redirect(url_for('invite_user'))

    return render_template('invite_user.html', user=current_user)

@app.route('/accept_invite/<token>', methods=['GET', 'POST'])
def accept_invite(token):
    s = URLSafeTimedSerializer(app.secret_key)
    
    all_users = User.query.all()

    try:
        email = s.loads(token, max_age=3600, salt='email-invite')  # Token expires after 1 hour
    except SignatureExpired:
        flash('The invitation link has expired.')
        return redirect(url_for('home'))
    except BadTimeSignature:
        flash('Invalid invitation link.')
        return redirect(url_for('home'))
    
    print("Email from token:", email)
    print("All emails in DB:", [u.email for u in all_users])

    if request.method == 'POST':
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenumber = request.form['phonenumber']
        company = request.form['company']
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')
        
        # Fetch the organization_id from the inviting user
        inviting_user = User.query.filter_by(email=email).first()
        
        if inviting_user is None:
            flash(f'Inviting user not found for email: {email}')
            return redirect(url_for('home'))
        
        if inviting_user.organization:
            organization_id = inviting_user.organization.id
        else:
            flash('Organization not found for inviting user.')
            return redirect(url_for('home'))

        # Create the new user
        new_user = User(
            email=email,
            password=hashed_password,
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
            company=company,
            organization_id=organization_id  # Setting the organization_id to be the same as the inviting user
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('You have successfully joined the organization.')
        return redirect(url_for('login'))
    
    return render_template('accept_invite.html', email=email, token=token, user=current_user)  # Removed 'user=current_user' as it's not used in this route


@app.route('/delete_empty_contacts', methods=['GET'])
@login_required
def delete_empty_contacts():
    # Query to find 'empty' contacts. Adjust the criteria as needed.
    empty_contacts = CRM.query.filter(
        (CRM.Contact == None) | (CRM.Contact == ''), 
        (CRM.PhoneEmail == None) | (CRM.PhoneEmail == '')
    ).all()

    for contact in empty_contacts:
        if contact.user_id == current_user.id:  # Ensure the user owns this contact
            db.session.delete(contact)

    db.session.commit()

    return redirect(url_for('crm'))

@app.route('/add_tag/<int:id>', methods=['POST'])
@login_required
def add_tag(id):
    contact = CRM.query.get_or_404(id)
    if contact.user_id != current_user.id:
        return 'You do not have permission to edit this contact'
        
    new_tag_name = request.form.get('new_tag').strip()
    if new_tag_name:  # Check if the tag is not empty
        # Check if the tag already exists, create if not
        tag = Tags.query.filter_by(name=new_tag_name).first()
        if tag is None:
            tag = Tags(name=new_tag_name)
            db.session.add(tag)
        
        # Add the new tag to the contact
        contact.tags.append(tag)
        db.session.commit()
        
    return redirect(url_for('contact_detail', id=id))

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact_to_delete = CRM.query.get_or_404(contact_id)

    # Make sure the current user owns the contact
    if contact_to_delete.user_id != current_user.id:
        return 'You do not have permission to delete this contact'

    try:
        db.session.delete(contact_to_delete)
        db.session.commit()
        return redirect(url_for('crm'))  # Redirecting to the list of contacts after deletion
    except:
        return 'There was an issue deleting that contact'

@app.route('/save_notes/<int:id>', methods=['POST'])
@login_required  # Assuming you're using Flask-Login
def save_notes(id):
    contact = CRM.query.get_or_404(id)
    if contact.user_id == current_user.id:
        due_date_str = request.form.get('due_date')
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        new_note = Note(
            content=request.form.get('notes'),
            contact_id=id,
            due_date=due_date,
            organization_id=current_user.organization_id  # new line
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('contact_detail', id=id))

# app.py
@app.route('/contact_detail/<int:id>')
@login_required
def contact_detail(id):
    contact = CRM.query.get_or_404(id)
    notes = Note.query.filter_by(contact_id=id, organization_id=current_user.organization_id).all()
    return render_template('contact_detail.html', contact=contact, notes=notes, user=current_user)


@app.route('/CRM', methods=['GET', 'POST'])
@login_required
def crm():
    if request.method == 'POST':
        csv_file_upload = request.files['csv']
        
        if not csv_file_upload:
            return "No file uploaded", 400

        if csv_file_upload:
            csvfilename = secure_filename(csv_file_upload.filename)
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
            csv_file_upload.save(saved_path)

            with open(saved_path, 'r') as f:
                csv_file = csv.DictReader(f)
                for row in csv_file:
                    tag_names = row.get('Tags', '').split(',')
                    tags = []
                    
                    for tag_name in tag_names:
                        tag_name = tag_name.strip()  # Remove any extra spaces
                        if tag_name:  # Skip empty or null strings
                            tag = Tags.query.filter_by(name=tag_name).first()
                            if tag is None:
                                tag = Tags(name=tag_name)
                                db.session.add(tag)
                            tags.append(tag)
                    contactname = row.get('First Name', '').strip()  # Assuming the CSV column is named "FirstName"
                    contactcompany = row.get('Company Name', '').strip()  # Assuming the CSV column is named "CompanyName"
                    if contactname or contactcompany:
                        new_contact = CRM(
                            Contact=row.get('First Name'),
                            PhoneEmail=row.get('PhoneEmail'),
                            tags=tags,
                            user_id=current_user.id,
                            contactlastname=row.get('Last Name'),
                            contactbillingaddress=row.get('Billing Address'),
                            contactbillingaddresscity=row.get('Billing Address City'),
                            contactbillingaddressstate=row.get('Billing Address State'),
                            contactbillingaddresscountry=row.get('Billing Address Country'),
                            contactbillingaddresszip=row.get('Billing Address Postal Code'),
                            leadstatus=row.get('Lead Status'),
                            contactemail=row.get('Email'),
                            contactphone=row.get('Phone'),
                            contactcompany=row.get('Company Name'),
                            organization_id=current_user.organization_id
                        )
                        db.session.add(new_contact)
                    db.session.commit()

    page = request.args.get('page', 1, type=int)
    
    contacts = (CRM.query
                .filter_by(organization_id=current_user.organization_id)
                .join(Note, isouter=True)  # Use outerjoin if you are using older SQLAlchemy
                .order_by(CRM.id, desc(Note.created_at))
                .paginate(page=page, per_page=10, error_out=False))

    # Create a dictionary to store the latest note for each contact
    latest_notes = {}
    for contact in contacts.items:
        if contact.notes:
            latest_notes[contact.id] = contact.notes[0].content

    next_url = url_for('crm', page=contacts.next_num) if contacts.has_next else None
    prev_url = url_for('crm', page=contacts.prev_num) if contacts.has_prev else None
    current_page = contacts.page
    total_pages = contacts.pages
    pages_to_show = 5
    pages = [page for page in range(current_page, min(current_page + pages_to_show, total_pages + 1))]
    
    return render_template('crm.html', contacts=contacts.items, latest_notes=latest_notes, next_url=next_url, prev_url=prev_url, pages=pages, total_pages=total_pages, user=current_user, current_page=current_page)

@app.route('/csv/<filename>')
def uploaded_csv(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pricing')
def pricing ():
    return render_template('pricing.html', user=current_user)

if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='127.0.0.1', port=port)

