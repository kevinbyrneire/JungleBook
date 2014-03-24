from flask.ext.wtf import Form
from flask import render_template
from wtforms import TextField, PasswordField, DateField, validators

class Login(Form):
	email = TextField('E-mail',[validators.Required()])
	password = PasswordField('Password',[validators.Required()])

class SignUp(Form):
	firstname = TextField('First Name',[validators.Required()])
	
	lastname = TextField('Last Name', [validators.Required()])

	nickname = TextField('Nickname',[validators.Optional()])

	email = TextField('E-mail',[validators.Required()])

	dob = DateField('DOB',[validators.Required(message='Please enter DOB in the required form')],format='%d/%m/%Y')

	hometown = TextField('Hometown',[validators.Optional()])

	password1 = PasswordField('Password',[validators.Required(),
	validators.EqualTo('password2',message='Passwords must match.'),
	validators.Length(min=5,max=30,message='Password must be minimum of 5 characters')])

	password2 = PasswordField('Confirm Password',[validators.Required()])

class EditProf(Form):
	firstname = TextField('First Name',[validators.Optional()])
	lastname = TextField('Last Name',[validators.Optional()])
	dob = DateField('DOB',[validators.Optional()],format='%d/%m/%Y')
	hometown = TextField('Hometown',[validators.Optional()])
	nickname = TextField('Nickname',[validators.Optional()])
    	def __init__(self, *args, **kwargs):
        	Form.__init__(self, *args, **kwargs)
        
	def validate(self):
		if not Form.validate(self):
            
			return False
		return True
        

class Search(Form):
	search=TextField('Search',[validators.Required()])

