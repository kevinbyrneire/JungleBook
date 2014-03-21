from flask import render_template, flash, redirect, session, url_for, request,g
from app import app, log_man, db, MAX_USERS
from app.models import User
from flask.ext.login import login_user, current_user,logout_user, login_required
from forms import Login,SignUp,EditProf,Search
from datetime import date

@log_man.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
	g.user=current_user
	if g.user.is_authenticated():
		g.search_form=Search()
		#db.session.add(g.user)
		#db.session.commit()
	#g.age=(date.today-g.user.dob).days/365
		#g.user.age = 20#(date.today()-g.dob)/365
@app.route('/')
def home():
	if g.user.is_authenticated():
		return redirect(url_for('list_users'))
	return redirect(url_for('sign_up'))

@app.route('/login',methods=['GET','POST'])
def login():
	
	if g.user is not None and g.user.is_authenticated():
		flash('You are already logged in as '+ g.user.first_name+' '+g.user.last_name)
		return redirect(url_for('home'))
	form=Login()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()

		if user is None:
			flash("Invalid e-mail address")

		elif form.password.data==user.password:
			login_user(user)
			flash("Login Successful. Welcome "+g.user.first_name)
			return redirect(url_for('profile',id=user.id))
		else:
			flash("Incorrect password!")

	return render_template('login.html',form=form)
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('home'))

@app.route('/signup',methods=['GET','POST'])
def sign_up():
	if g.user is not None and g.user.is_authenticated():
		flash('You are already logged in as '+ g.user.first_name+' '+g.user.last_name)
		return redirect(url_for('home'))
	form = SignUp()
	if form.validate_on_submit():
		if User.query.filter_by(email=form.email.data).count()==0:
			user = User(first_name = form.firstname.data,
				last_name=form.lastname.data,nickname = form.nickname.data, email=form.email.data,
				dob=form.dob.data, home=form.hometown.data, password=form.password1.data)
			db.session.add(user)
			db.session.commit()
			login_user(user)
			flash("You have successfully signed up. Welcome "+user.first_name)
			return redirect(url_for('home'))
		flash("This email address is already in use. Please enter a valid email address")
	return render_template('signup.html',form=form)

@app.route('/profile/<id>')
@login_required
def profile(id):
	x = User.query.get(id)
	if x is None:
		flash('Not a valid user.')
		return redirect(url_for('home'))
	age = (date.today()-x.dob).days/365
	return render_template('profile.html',user=x,age=age)

@app.route('/add_friend/<id>')
@login_required
def add_friend(id):
	new = User.query.get(id)
	if new is None:
		flash('That is not a valid user-id.')
		return redirect(url_for('home'))
	#frndshp = g.user.add_friend(new)
	#db.session.add(frndshp)
	db.session.add(g.user.add_friend(new))
	db.session.commit()
	flash('You are now friends with '+new.first_name+' '+new.last_name)
	return redirect(url_for('profile',id=new.id))

@app.route('/remove_friend/<id>')
@login_required
def remove_friend(id):
	exfriend = User.query.get(id)
	x=g.user.remove_friend(exfriend)
	db.session.add(x)
	db.session.commit()
	flash('Your are no longer friends with ' + exfriend.first_name)
	return redirect(url_for('home'))

@app.route('/friends/<id>')
@login_required
def show_friends(id):
	return render_template('friends.html',user=User.query.get(id))

@app.route('/edit/<id>',methods = ['GET','POST'])
@login_required
def edit(id):
	if int(id)!=g.user.id:
		flash('You are not authorized to edit this profile')
		return redirect(url_for('home'))
	form=EditProf()
	if form.validate_on_submit():
		if form.firstname.data: g.user.first_name=form.firstname.data
		if form.lastname.data: g.user.last_name=form.lastname.data
		if form.nickname.data: g.user.nickname=form.nickname.data
		if form.dob.data: g.user.dob=form.dob.data
		if form.hometown.data: g.user.home=form.hometown.data
		db.session.add(g.user)
		db.session.commit()
		#flash(form.nickname.data +' ' + g.user.nickname)
		#db.session.commit()
		return redirect(url_for('profile',id=g.user.id))
	return render_template('edit.html',form=form)

@app.route('/search',methods=['POST'])
@login_required
def search():
	if g.search_form.validate_on_submit():
		return redirect(url_for('search_results',criteria=g.search_form.search.data))
	flash('something is wrong')
	return redirect(url_for('home'))

@app.route('/search_results/<criteria>')
@login_required
def search_results(criteria):
	return render_template('search.html',results=User.query.filter_by(first_name=criteria).all())

@app.route('/users')
@app.route('/users/<int:page>')
@login_required
def list_users(page=1):
	#if sortby=='friends':
		#return render_template('index.html',users=User.query.order_by(User.count_friends()))
	return render_template('index.html', users=User.query.order_by(User.last_name).paginate(page,MAX_USERS,False))



#if __name__=='__main__':
#	app.run()

