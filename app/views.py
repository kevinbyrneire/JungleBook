from flask import render_template, flash, redirect, session, url_for, request,g
from app import app, log_man, db, MAX_USERS # db is the database.
from app.models import User
from flask.ext.login import login_user, current_user,logout_user, login_required
from forms import Login,SignUp,EditProf,Search
from datetime import date # need date to calculate user's age.
from sqlalchemy import desc #need to list users in descending order of friend count.
  

@log_man.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
# use the global g variable so we can access the current user in templates.
def before_request():
	g.user=current_user 




# the main home page. displays either list of users or signup page if not signed in.#
@app.route('/') 
def home():
	if g.user.is_authenticated():
		return redirect(url_for('list_users'))
	return redirect(url_for('sign_up'))




# The homepage redirects to here if there is a user signed in.
# Simply displays all the users on the network, with various sorting options and pagination. #
@app.route('/users')
@app.route('/users/<int:page>/<int:stype>')
@login_required
def list_users(page=1,stype=1):
	sort = {1:User.last_name,2:User.first_name,3:desc(User.friend_count)}
	if stype in [1,2,3]:
		return render_template('index.html', users=User.query.order_by(sort[stype]).paginate(page,MAX_USERS,False))
	return redirect(url_for('home'))




#The signup page. Here, a user sets up an account by enetring their profile info.
@app.route('/signup',methods=['GET','POST'])
def sign_up():
	if g.user is not None and g.user.is_authenticated():
		flash('You are already logged in as '+ g.user.first_name+' '+g.user.last_name)
		return redirect(url_for('home'))
	form = SignUp()
	if form.validate_on_submit():

		if User.query.filter_by(email=form.email.data).count()==0: #ensure the email isn't already used.
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




# the login page. 
@app.route('/login',methods=['GET','POST'])
def login():
	
	if g.user is not None and g.user.is_authenticated(): # if user is already logged in go to home page.
		flash('You are already logged in as '+ g.user.first_name+' '+g.user.last_name)
		return redirect(url_for('home'))
	
	form=Login()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first() #query the database,filter by email.

		if user is None:
			flash("Invalid e-mail address")

		elif form.password.data==user.password:
			login_user(user)
			flash("Login Successful. Welcome "+g.user.first_name)
			return redirect(url_for('profile',id=user.id))
		else:
			flash("Incorrect password!")

	return render_template('login.html',form=form)




# the logout page. User must be logged in to access this page.
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('login'))





# Users' profiles. A user must be signed in to view other profiles.
@app.route('/profile/<id>')
@login_required
def profile(id):
	user = User.query.get(id)
	if user is None:
		flash('Not a valid user.')
		return redirect(url_for('home'))

	age = (date.today()-user.dob).days/365 #calculate the user's age.

	return render_template('profile.html',user=user,age=age)





# The method for adding friends.
@app.route('/add_friend/<id>')
@login_required
def add_friend(id):
	new = User.query.get(id) # this is the user that will be added to the signed in user's friends.
	if new is None:
		flash('That is not a valid user-id.')
		return redirect(url_for('home'))

	db.session.add(g.user.add_friend(new)) # use the add_friend() method from models.py
	db.session.commit()
	
	if g.user.is_friend(new): flash('You are now friends with '+new.first_name+' '+new.last_name)
	else: flash('Friend request sent to ' + new.first_name+' '+new.last_name)
	
	return redirect(url_for('profile',id=new.id))





#Method for removing users from the friends list.
@app.route('/remove_friend/<id>')
@login_required
def remove_friend(id):
	exfriend = User.query.get(id) #this is the friend we want to remove.
	x=g.user.remove_friend(exfriend)
	db.session.add(x)
	db.session.commit()
	flash('Your are no longer friends with ' + exfriend.first_name)
	return redirect(url_for('home'))




@app.route('/add_bestie/<id>')
@login_required
def add_bestie(id):
	best = User.query.get(id)
	db.session.add(g.user.add_best(best))
	db.session.commit()
	flash('You are now best friends with '+best.first_name+' '+best.last_name)
	return redirect(url_for('home'))



# This page displays the list of friends of a user.
@app.route('/friends/<id>')
@login_required
def show_friends(id):
	return render_template('friends.html',user=User.query.get(id))

@app.route('/requests')
@login_required
def show_requests():
	return render_template('requests.html')



# This is the page for editing a profile.
# A user can only edit their own profile and no-one else's.
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

		return redirect(url_for('profile',id=g.user.id))

	return render_template('edit.html',form=form)






# If a user wants to delete their account they are redirected here to confirm.
@app.route('/confirm')
@login_required
def confirm_del():
	return render_template('confirmation.html')


# If confirmation is given then the user is redirected here and their account is deleted.
@app.route('/remove')
@login_required
def remove_acc():	
	db.session.delete(g.user)
	db.session.commit()
	flash('Your account has been deleted')
	return redirect(url_for('home'))

