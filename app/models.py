from app import db
from sqlalchemy import func,select,or_
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from app import app

friend = db.Table('friend',
	db.Column('id_1',db.Integer,db.ForeignKey('user.id')),
	db.Column('id_2' ,db.Integer,db.ForeignKey('user.id')))
	


besties = db.Table('besties',
	db.Column('id_1', db.Integer,db.ForeignKey('user.id')),
	db.Column('id_2', db.Integer,db.ForeignKey('user.id')))

requests = db.Table('requests',
	db.Column('id_1',db.Integer,db.ForeignKey('user.id')),
	db.Column('id_2' ,db.Integer,db.ForeignKey('user.id')))

class User(db.Model):
	
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(50),unique=False)
	last_name= db.Column(db.String(50),unique=False)
	nickname = db.Column(db.String(50),unique=False)
	email = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	dob=db.Column(db.Date)

	home = db.Column(db.String(50),unique=False)

	besty = db.relationship('User',secondary=besties, uselist = False, primaryjoin=(id==besties.c.id_1),
	secondaryjoin=(id==besties.c.id_2),backref=db.backref('bestie',lazy='dynamic'))

	friends = db.relationship('User',secondary=friend,primaryjoin=(id==friend.c.id_1),
	secondaryjoin=(id==friend.c.id_2),backref=db.backref('friend',lazy='dynamic'),lazy='dynamic')

	asked = db.relationship('User',secondary=requests, primaryjoin=(id==requests.c.id_1),
	secondaryjoin=(id==requests.c.id_2), backref=db.backref('pending',lazy='dynamic'),lazy='dynamic')


	def __init__(self, first_name=None,last_name=None, nickname = None, email=None,home=None, password=None,dob=None,best=None):
		self.first_name = first_name
		self.last_name=last_name
		self.nickname = nickname
		self.email = email
		self.dob = dob
		self.password = password
		self.home=home
		self.besty = best

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def is_requested(self,my_friend):
		return self.pending.filter(requests.c.id_1==my_friend.id).count()>0


	def is_friend(self,my_friend):
		return self.friends.filter(friend.c.id_2==my_friend.id).union(self.friend.filter(friend.c.id_1==my_friend.id)).count()>0
	

	def add_friend(self,new_friend):
		if not(self.is_friend(new_friend)):
			if self.is_requested(new_friend):
				self.pending.remove(new_friend)
				self.friends.append(new_friend)
			
			elif self.asked.filter(requests.c.id_2==new_friend.id).count()==0:
				
				self.asked.append(new_friend)

			return self

	def add_best(self,my_friend):
		if self.is_friend(my_friend):
			self.besty=my_friend
		return self

	
	def remove_friend(self,my_friend):
		if self.is_friend(my_friend):
			if my_friend in self.friends.all():
				self.friends.remove(my_friend)
			else:
				self.friend.remove(my_friend)
		if self.besty==my_friend:
			self.besty=None
		return self		

	def list_friends(self):
		return self.friends.union(self.friend).order_by(User.last_name).all()
	

	@hybrid_property
	def friend_count(self):
		return self.friends.count()+self.friend.count()
	
	@friend_count.expression
	def friend_count(cls):
		return select([func.count(friend.c.id_1)]).where(or_(friend.c.id_2==cls.id,friend.c.id_1==cls.id))
