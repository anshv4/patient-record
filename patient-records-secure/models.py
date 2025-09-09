
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default="clinician")  # admin, clinician
    active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Keep name non-encrypted for search convenience; encrypt other PHI fields
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20))

    # Encrypted bytes fields
    address_enc = db.Column(db.LargeBinary)
    phone_enc = db.Column(db.LargeBinary)
    medical_history_enc = db.Column(db.LargeBinary)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    clinician_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    visit_date = db.Column(db.Date, nullable=False)
    reason_enc = db.Column(db.LargeBinary)
    notes_enc = db.Column(db.LargeBinary)

    patient = db.relationship('Patient', backref=db.backref('visits', lazy=True))
    clinician = db.relationship('User')

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # read, create, update, delete, login, logout
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    meta_data = db.Column(JSON, default={})
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
