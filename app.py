# let's import the flask
from flask import Flask, render_template, request, redirect, url_for, session
import os # importing operating system module
import os
from my_package.__init__ import create_app
from flask_login import LoginManager
from flask_login import current_user,login_required
from my_package.models import CRM, User, db, Note, Tags
from flask import send_from_directory
import csv
from werkzeug.utils import secure_filename
from sqlalchemy import desc

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
        new_note = Note(content=request.form.get('notes'), contact_id=id, due_date=due_date)
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('contact_detail', id=id))

@app.route('/upcoming_due_dates')
@login_required
def upcoming_due_dates():
    current_time = datetime.utcnow()
    contacts_with_due_dates = (db.session.query(CRM, Note)
                                .join(Note, Note.contact_id == CRM.id)
                                .filter(Note.due_date > current_time)
                                .order_by(Note.due_date.asc())
                                .all())
    return render_template('upcoming_due_dates.html', contacts_with_due_dates=contacts_with_due_dates)

# app.py
@app.route('/contact_detail/<int:id>')
@login_required
def contact_detail(id):
    contact = CRM.query.get_or_404(id)
    notes = Note.query.filter_by(contact_id=id).all()
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
                    
                    new_contact = CRM(
                        Contact=row.get('Contact'),
                        PhoneEmail=row.get('PhoneEmail'),
                        tags=tags,
                        user_id=current_user.id
                    )
                    db.session.add(new_contact)
                db.session.commit()

    page = request.args.get('page', 1, type=int)
    
    contacts = (CRM.query
                .filter_by(user_id=current_user.id)
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

