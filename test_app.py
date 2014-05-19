#!flask/bin/python
from app import app, db
from app.models import User
from sqlalchemy import and_
import pytest
import os
from datetime import date
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://kev:password@localhost/kev"# = 'sqlite:///' + os.path.join(basedir, 'test.db')
db.create_all()

@pytest.fixture(scope='module')
def users():
	''' Create a list of test users '''
	return User.query.filter(and_(User.first_name=='Test',User.last_name=='Test')).all()

class Test():
	@classmethod
	def setup_class(cls):
		''' Add some test users to the database '''
		x1 = User(first_name='Test',last_name = 'Test',email='test1@gmail.com',dob=date(1990,1,1))
		x2 = User(first_name='Test',last_name = 'Test',email='test2@gmail.com',dob=date(1990,1,1))
		x3 = User(first_name='Test',last_name = 'Test',email='test3@gmail.com',dob=date(1990,1,1))
		for i in [x1,x2,x3]:
			db.session.add(i)
		db.session.commit()

	@classmethod
	def teardown_class(cls):
		''' Remove the test users '''
		for i in User.query.filter(and_(User.first_name=='Test',User.last_name=='Test')).all():
			db.session.delete(i)
		db.session.commit()

	


	def test_friends(self,users):
		x1=users[0]
		x2=users[1]
		assert not x1.is_friend(x2)
		assert x1.friend_count==0

		db.session.add(x1.add_friend(x2))
		db.session.commit()

		assert x1.friend_count==0 #both users should still have no friends as confirmation is required
		assert x2.friend_count==0

		assert x2.is_requested(x1)

		db.session.add(x2.add_friend(x1)) # adding the friendship in the reverse direction confirms friendship
		db.session.commit()

		assert x1.is_friend(x2) # the two users should now be friends with eachother
		assert x2.is_friend(x1)

		assert x1.friend_count==1
		assert x2.friend_count==1
		
		db.session.add(x1.remove_friend(x2))
		db.session.commit()

		assert not x1.is_friend(x2)
		assert not x2.is_friend(x1)



	def test_besty(self,users):
		x1=users[0]
		x2=users[1]
		x3=users[2]
		
		x1.friends.append(x2) #users must first be friends to become best friends
		x1.friends.append(x3)
		db.session.add(x1)
		db.session.commit()

		db.session.add(x1.add_best(x2)) #make x2 the best friend of x1
		db.session.commit()

		assert x1.besty is x2

		db.session.add(x1.add_best(x3)) #make x3 the besty of x1
		db.session.commit()
	
		assert x1.besty is x3 #ensure x1 still only has one best friend


