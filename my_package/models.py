from .__init__ import db
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func

class CRM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contactname = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_phone_and_email = db.Column(db.String(10000))
    contact_tags = db.Column(db.String(10000))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    phonenumber = db.Column(db.String(20))
    company = db.Column(db.String(150))
    crm = db.relationship('CRM')  # Changed from 'Note' to 'CRM'
