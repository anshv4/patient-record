
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Login")

class PatientForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    dob = DateField("Date of Birth", validators=[DataRequired()], format="%Y-%m-%d")
    gender = SelectField("Gender", choices=[("male","Male"),("female","Female"),("other","Other")])
    address = TextAreaField("Address")
    phone = StringField("Phone")
    medical_history = TextAreaField("Medical History")
    submit = SubmitField("Save")

class VisitForm(FlaskForm):
    visit_date = DateField("Visit Date", validators=[DataRequired()], format="%Y-%m-%d")
    reason = StringField("Reason")
    notes = TextAreaField("Notes")
    submit = SubmitField("Save")
