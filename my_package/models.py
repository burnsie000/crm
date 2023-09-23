from .__init__ import db, metadata
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Integer, ForeignKey, MetaData

# Define a many-to-many table for the relationship between CRM and Tag
crm_tags = Table('crm_tags', db.Model.metadata,
    Column('crm_id', Integer, ForeignKey('CRM.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('Tags.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    phonenumber = db.Column(db.String(20))
    company = db.Column(db.String(150))
    crm = db.relationship('CRM', back_populates='user')  # Changed from 'Note' to 'CRM'

class CRM(db.Model):
    __tablename__ = 'CRM'
    id = db.Column(db.Integer, primary_key=True)
    contactname = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    Contact = db.Column(db.String(10000))
    PhoneEmail = db.Column(db.String(10000))
    tags = db.relationship('Tags', secondary=crm_tags, lazy='subquery', back_populates='contacts')
    notes = db.relationship('Note', backref='contact', lazy=True)
    user =db.relationship('User', back_populates='crm')

class Tags(db.Model):
    __tablename__ = 'Tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    contacts = db.relationship('CRM', secondary=crm_tags, lazy='subquery', back_populates='tags')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    contact_id = db.Column(db.Integer, db.ForeignKey('CRM.id'))
    due_date = db.Column(db.DateTime, nullable=True)


   
