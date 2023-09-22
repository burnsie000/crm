# let's import the flask
from flask import Flask, render_template, request, redirect, url_for, session
import os # importing operating system module
import os
from my_package.__init__ import create_app
from flask_login import LoginManager
from flask_login import current_user
from my_package.models import CRM, User, db
from flask import send_from_directory
import csv
from werkzeug.utils import secure_filename

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

@app.route('/CRM', methods=['GET', 'POST'])
def crm ():
    if request.method == 'POST':
        csv_file_upload = request.files['csv']
        
        if not csv_file_upload:
            return "No file uploaded", 400

        # Wrap the FileStorage object in a TextIOWrapper so we can read it as text
        if csv_file_upload:
            csvfilename = secure_filename(csv_file_upload.filename)
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], csvfilename)
            csv_file_upload.save(saved_path)

            with open(saved_path, 'r') as f:
                csv_file = csv.DictReader(f)
                for row in csv_file:
                    new_contact = CRM(
                        Contact=row.get('Contact'),
                        PhoneEmail=row.get('PhoneEmail'),
                        Tags=row.get('Tags')
                    )
                    db.session.add(new_contact)
                db.session.commit()

    page = request.args.get('page', 1, type=int)
    contacts = CRM.query.paginate(page=page, per_page=10, error_out=False)
    next_url = url_for('crm', page=contacts.next_num) if contacts.has_next else None
    prev_url = url_for('crm', page=contacts.prev_num) if contacts.has_prev else None
    current_page = contacts.page  # Current page number
    total_pages = contacts.pages  # Total number of pages
    pages_to_show = 5  # Number of pages to show in the pagination control
    pages = [page for page in range(current_page, min(current_page + pages_to_show, total_pages + 1))]
    return render_template('crm.html', contacts=contacts.items, next_url=next_url, prev_url=prev_url, pages=pages, total_pages=total_pages, user=current_user, current_page=current_page)

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

