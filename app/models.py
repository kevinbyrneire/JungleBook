from app import db
from app import app
#import flask.ext.whooshalchemy as whooshalchemy
friend = db.Table('friend',
	db.Column('id_1',db.Integer,db.ForeignKey('user.id')),
	db.Column('id_2' ,db.Integer,db.ForeignKey('user.id')))
	#db.Column('are_besties' ,db.Boolean))
	
	

class User(db.Model):
	
	__tablename__ = 'user'
	#__searchable__=['first_name','last_name']
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(50),unique=False)
	last_name= db.Column(db.String(50),unique=False)
	nickname = db.Column(db.String(50),unique=False)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	dob=db.Column(db.Date)
	home = db.Column(db.String(50),unique=False)
	#bestie = db.Column(db.Integer, db.ForeignKey('user.id'))
	#besties = db.relationship('User',secondary=friend,uselist=False,primaryjoin=(id==friend.c.id_2 or id==friend.c.id_1),
	#secondaryjoin=(friend.c.are_besties),backref=db.backref('bestie',uselist=False))

	friends = db.relationship('User',secondary=friend,primaryjoin=(id==friend.c.id_1),
	secondaryjoin=(id==friend.c.id_2),backref=db.backref('friend',lazy='dynamic'),lazy='dynamic')


	#bst_frnd = db.relationship('User',uselist=False)
	

	def __init__(self, first_name=None,last_name=None, nickname = None, email=None,home=None, password=None,dob=None):
		self.first_name = first_name
		self.last_name=last_name
		self.nickname = nickname
		self.email = email
		self.dob = dob
		self.password = password
		self.home=home
		#self.besties = bestfriend

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)


	def is_friend(self,my_friend):
		return self.friends.filter(friend.c.id_2==my_friend.id).union(self.friend.filter(friend.c.id_1==my_friend.id)).count()>0
	

	def add_friend(self,new_friend):
		if not(self.is_friend(new_friend)):
			self.friends.append(new_friend)
			return self

	def add_best(my_friend):
		self.besties=my_friend
		return self

	
	def remove_friend(self,my_friend):
		if self.is_friend(my_friend):
			if my_friend in self.friends.all():
				self.friends.remove(my_friend)
			else:
				self.friend.remove(my_friend)
		return self		

	def list_friends(self):
		return self.friends.union(self.friend).order_by(User.last_name).all()
	
	def count_friends(self):
		return self.friends.count()+self.friend.count()


#	def __repr__(self):
#		return '<User %r>' % (self.first_name)
#from app import app
#whooshalchemy.whoosh_index(app, User)
