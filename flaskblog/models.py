from flaskblog import db, login_manager
from datetime import datetime
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


class User(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(20), unique=True, nullable=False)
   email = db.Column(db.String(120), unique=True, nullable=False)
   password =  db.Column(db.String(60), nullable=False)
   posts = db.relationship('Post', backref='author', lazy=True)
   

   def __repr__(self):
      return f"User('{self.username}', '{self.email})"

class Post(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(100), nullable=False)
   content = db.Column(db.Text, nullable=False)
   date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   like_count = db.Column(db.Integer, nullable=False, default=0)
   category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   comments = db.relationship('Comment', backref='comment', lazy=True) 
  
   def __repr__(self):
      return f"Post('{self.title}', '{self.date_posted}')"


class Category(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(300), unique=True, nullable=False)
   post = db.relationship('Post', backref='category', lazy=True)

   def __repr__(self):
      return f"Category('{self.id}', '{self.name}')"



class Comment(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), unique=False)
   email = db.Column(db.String(120), unique=False, nullable=False)
   message = db.Column(db.Text, nullable=False)
   date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   status = db.Column(db.Boolean, default=False) # used for showed after approve 
   post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
   post = db.relationship('Post', backref=db.backref('post', lazy=True))

   def __repr__(self):
      return f"Comment('{self.name}', '{self.email}', '{self.message}')"

class Todo(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   task = db.Column(db.String(500), unique=False)
   date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

   def __repr__(self):
      return f"Todo('{self.id}', '{self.task}', '{self.date}')"