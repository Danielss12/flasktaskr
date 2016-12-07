import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = ' test.db'

class AllTests(unittest.TestCase):
	#executed prior to each test
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
		self.app = app.test_client()
		db.create_all()


	#executed after each test
	def tearDown(self):
		db.session.remove()
		db.drop_all()


	#each test should start with 'test'
	def test_user_setup(self):
		new_user = User("michael", "michael@mherman.org","michaelherman")
		db.session.add(new_user)
		db.session.commit()
		test = db.session.query(User).all()
		for t in test:
			t.name
		assert t.name == "michael"	


	# test to see if the form is present on login page
	def test_form_present_on_login_page(self):
		response = self.app.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please login to access your task list', response.data)


	# test to see if unregisteres users cannot login
	#helper method
	def login(self, name, password):
		return self.app.post('/', data = dict(name=name, password=password), follow_redirects=True)


	def test_users_cant_login(self):
		response = self.login('foo', 'bar')
		self.assertIn(b'Invalid username or password', response.data)



	#registered users can login
	#helper method
	def register(self, name, email, password, confirm):
		return self.app.post('register/',
		 data = dict(name=name, email=email, password=password, confirm=confirm), follow_redirects=True)

	def test_user_can_login(self):
		self.register('Michael', 'michael@realpython.com', 'python', 'python')
		response = self.login('Michael', 'python')
		self.assertIn(b'Welcome!', response.data)

	#add bad data to see how far the process gets
	def test_invalid_form_data(self):
		self.register('Michael','michael@realpython.com', 'python', 'python')
		response = self.login('alert("alert box!");', 'foo')
		self.assertIn(b'Invalid username or password.', response.data)

	#form is present on register page
	def test_form_is_present(self):
		response = self.app.get('register/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Please register to access the task list.', response.data)

	# users can register
	def test_user_registration_error(self):
		self.app.get('register/', follow_redirects=True)
		self.register('Michael', 'michael@realpython.com', 'python', 'python')
		self.app.get('register/', follow_redirects=True)
		response = self.register('Michael', 'michael@realpython.com', 'python', 'python')
		self.assertIn(b'That username and/or email already exist.', response.data)

    #helper method
	def logout(self):
		return self.app.get('logout/', follow_redirects=True)

	#test logging out for both logged in and not logged in users:
	def test_logged_in_users_can_logout(self):
		self.register('Fletcher', 'fletcher@realpython.com','python101','python101')
		self.login('Fletcher', 'python101')
		response = self.logout()
		self.assertIn(b'Goodbye!', response.data)

	def test_not_logged_in_users_cannot_logout(self):
		response = self.logout()
		self.assertNotIn(b'Goodbye!', response.data)

	#users can access tasks
	def test_logged_in_users_can_access_tasks(self):
		self.register('Fletcher', 'fletcher@realpython.com','python101','python101')
		self.login('Fletcher', 'python101')
		response = self.app.get('tasks/')
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'Add a new task:', response.data)

	def test_not_logged_in_users_cannot_access_tasks_page(self):
		response = self.app.get('tasks/', follow_redirects=True)
		self.assertIn(b'You need to login first.', response.data)

	#HELPER METHODS
	def create_user(self, name, email, password):
		new_user = User(name=name, email=email, password=password)
		db.session.add(new_user)
		db.session.commit()

	def create_task(self):
		return self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='02/05/2014',
			priority='1',
			posted_date='02/04/2014',
			status='1'
			),follow_redirects=True)

	#users can add tasks
	def test_users_can_add_tasks(self):
		self.create_user('Michael','michael@realpython.com','python')
		self.login('Michael', 'python')
		self.app.get('tasks/',follow_redirects=True)
		response= self.create_task()
		self.assertIn(b'New entry was successfully posted, Thank you!', response.data)

    #what if there's an error
	def test_users_cannot_add_tasks_when_error(self):
		self.create_user('Michael','michael@realpython.com','python')
		self.login('Michael', 'python')
		self.app.get('tasks/',follow_redirects=True)
		response = self.app.post('add/', data=dict(
			name='Go to the bank',
			due_date='',
			priority='1',
			posted_date='02/205/2014',
			status='1'
			), follow_redirects=True)
		self.assertIn(b'This field is required.', response.data)

	# users can complete tasks
	def test_users_can_complete_tasks(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get("complete/1/", follow_redirects=True)
		self.assertIn(b'The task is complete. Nice job!', response.data)

	# users can delete tasks
	def test_users_can_delete_tasks(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		response = self.app.get("delete/1/", follow_redirects=True)
		self.assertIn(b'The task was deleted, why not add a new one?', response.data)

	def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
		self.create_user('Michael', 'michael@realpython.com', 'python')
		self.login('Michael', 'python')
		self.app.get('tasks/', follow_redirects=True)
		self.create_task()
		self.logout()
		self.create_user('Fletcher', 'fletcher@realpython.com', 'python101')
		self.login('Fletcher', 'python101')
		self.app.get('tasks/', follow_redirects=True)
		response = self.app.get("complete/1/", follow_redirects=True)
		self.assertNotIn(b'The task is complete. Nice job!', response.data)











if __name__ == "__main__":
	unittest.main()