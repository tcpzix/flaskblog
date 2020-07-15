import os
import secrets
from sqlalchemy import desc
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post, Comment, Todo, Category
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm
from flask import render_template, url_for, flash, redirect, request, abort, jsonify, make_response


@app.route('/')
@app.route('/home')
def home():
   page = request.args.get('page', 1, type=int)
   #query last post first with desc
   posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=7)
   return render_template('index.html', title="tcpzix", posts=posts)

@app.route('/sample')
def sample():
   return render_template('work-samples.html', title='نمونه کار')

@app.route('/about')
def about():
   return render_template('about.html', title="درباره من")

@app.route('/resume')
def resume():
   return render_template('resume.html', title='رزومه')

@app.route('/contact')
def contact():
   return render_template('contact.html', title='تماس')

@app.route('/linux')
def linux_article():
   page = request.args.get('page', 1, type=int)
   posts = Post.query.filter_by(category_id=1).paginate(page=page, per_page=5)
   return render_template('linux.html', title='لینوکس', posts=posts) 

@app.route('/python')
def python_article():
   page = request.args.get('page', 1, type=int)
   posts = Post.query.filter_by(category_id=2).paginate(page=page, per_page=5)
   return render_template('python.html', title='پایتون', posts=posts)

@app.route('/voip')
def voip_article():
   page = request.args.get('page', 1, type=int)
   posts = Post.query.filter_by(category_id=3).paginate(page=page, per_page=5)
   return render_template('voip.html', title='ویپ', posts=posts)

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
   if current_user.is_authenticated:
      return redirect(url_for('home'))
   form = RegistrationForm()
   if form.validate_on_submit ():
      hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      user = User(username=form.username.data, email=form.email.data, password=hashed_password)
      db.session.add(user)
      db.session.commit()
      flash('Your Account has been created')
      return redirect(url_for('login'))
   return render_template('register.html', title='Register', form=form)

# Login User 
@app.route('/login', methods=['GET', 'POST'])
def login():
   if current_user.is_authenticated:
      return redirect(url_for('home'))
   form = LoginForm()
   if form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      if user and bcrypt.check_password_hash(user.password, form.password.data):
         login_user(user, remember=form.remember.data)
         # take next variable data in url (redirect to requested login_required page after login)
         next_page = request.args.get('next')
         # ternary conditional
         return redirect(next_page) if next_page else redirect(url_for('panel'))
      else:
         flash('Wrong Password...!')
         return redirect(url_for('login'))
   return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
   logout_user()
   return redirect(url_for('home'))


# Write New Post
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
   data = request.get_json()
   title = data['title']
   category = data['category']
   content = data['content']
   print('category: ', category)
   post = Post(title=title, content=content, category_id=category, author=current_user)

   db.session.add(post)
   db.session.commit()
   return jsonify('post created')

# show Post
@app.route('/post/<int:post_id>', methods=['GET'])
def post(post_id):
   post = Post.query.get_or_404(post_id)
   comments = Comment.query.filter_by(post_id=post_id).all()
   return render_template('post.html', post=post, comments=comments)

# Like Post 
@app.route('/like/<int:post_id>' , methods=['GET'])
def like(post_id):
   post = Post.query.get_or_404(post_id)
   post.like_count += 1
   db.session.commit()
   return jsonify(post.like_count)

# Add Post Comment
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
   data = request.get_json()
   name = data['name']
   email = data['email']
   message = data['message']
   comment = Comment(name=name, email=email, message=message, post_id=post_id)
   db.session.add(comment)
   db.session.commit()
   return jsonify('comment recievd!')

# Update Post
@app.route('/editpost/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
   post = Post.query.get_or_404(post_id)
   if post.author != current_user:
      return jsonify('You Are Not Access To Do This...!')
      abort(403)
   if request.method == 'GET':
      title = post.title
      content = post.content
      res = {'title':title, 'content':content}
   elif request.method == 'POST':
      data = request.get_json()
      # spliting the recived data 
      print(data)
      title = data['title']
      category = data['category']
      content = data['content']
      # edit post in db
      post.title = title
      post.category_id = category
      post.content = content
      db.session.commit()

      res = 'post updated...'

   return jsonify(res)


# Delete Post
@app.route('/delpost', methods=['POST'])
@login_required
def delete_post():
   data = request.get_json()
   post = Post.query.get_or_404(data)
   if post.author != current_user:
      return jsonify('You Have Not Access To Do This...!')
   
   # First should Delelte Comment for post
   comment = Comment.query.filter_by(post_id=data).delete()

   # if post.author != current_user:
   #    return jsonify('You have No Access To Do This.....!')
   #    abort(403)
  
   db.session.delete(post)
   db.session.commit()
   return jsonify(f'post with id {post.id} deleted....')

 
# panel index
@app.route('/panel')
@login_required
def panel():
   # Count the Rows of Table
   total_post = Post.query.count()
   total_comment = Comment.query.count()
   total_user = User.query.count()
   # For render in new post form
   categories = Category.query.all()
   # Query last 3 Column
   last_3posts = Post.query.order_by(Post.id.desc()).limit(3).all() 
   last_3comments = Comment.query.order_by(Comment.id.desc()).limit(3).all()
   todo_list = Todo.query.all()
   return render_template('/blogpanel/index.html', title='Site Panel', 
               total_post = total_post, 
               total_comment = total_comment, 
               total_user = total_user, 
               last_posts = last_3posts, 
               last_comments = last_3comments,
               todo_list = todo_list, 
               categories = categories)



@app.route('/addtodo', methods=['POST'])
@login_required
def add_todo():
   data = request.get_json()
   todo = Todo(task = data)
   db.session.add(todo)
   db.session.commit()
   return jsonify('task added!')


@app.route('/deltodo', methods=['POST'])
@login_required
def del_todo():
   data = request.get_json()
   todo = Todo.query.get_or_404(data)
   db.session.delete(todo)
   db.session.commit()
   return jsonify('deleted')


@app.route('/posts')
@login_required
def posts():
   page = request.args.get('page', 1, type=int)
   categories = Category.query.all()
   #query last post first with desc
   posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
   return render_template('/blogpanel/posts.html', title='allposts', posts=posts, categories = categories)


@app.route('/categories')
@login_required
def categories():
   categories = Category.query.all()
   return render_template('/blogpanel/categories.html', categories=categories)



@app.route('/addcategory', methods=['POST'])
@login_required
def add_category():
   data = request.get_json()
   db.session.add(Category(name=data))
   db.session.commit()
   return jsonify('New Category Added...!')


@app.route('/del-category', methods=['POST'])
@login_required
def del_category():
   catid = request.get_json()
   category = Category.query.get_or_404(catid)
   db.session.delete(category)
   db.session.commit()
   print(category)
   return jsonify(f'Category {category.name} Deleted...!')


@app.route('/edit-category/<int:cat_id>', methods=['GET', 'POST'])
@login_required
def edit_category(cat_id):
   category = Category.query.get_or_404(cat_id)
   if request.method == 'GET':
      res = category.name
   elif request.method == 'POST':
      data = request.get_json()
      category.name = data
      db.session.commit()
      res = f'Category {category.name} changed to {data}...!'
   return jsonify(res)


@app.route('/comments')
@login_required
def comments():
   comments= Comment.query.all()
   return render_template('/blogpanel/comments.html', comments=comments)


@app.route('/users')
@login_required
def users():
   users = User.query.all()
   return render_template('/blogpanel/users.html', users=users)



@app.route('/adduser', methods=['POST'])
@login_required
def adduser():
   data = request.get_json()
   username = data['name']
   email = data['email']
   password = data['password']
   hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
   user = User(username=username, email=email, password=hashed_password)
   db.session.add(user)
   db.session.commit()
   return jsonify('New User Added...!')



@app.route('/deluser', methods=['POST'])
def deluser():
   userid = request.get_json()
   print('User id' , userid)
   user = User.query.get_or_404(userid)
   db.session.delete(user)
   db.session.commit()
   return jsonify(f'User {user} Deleted...!')



@app.route('/changepass', methods=['POST'])
@login_required
def change_pass():
   data = request.get_json()
   oldpass = data['oldpass']
   newpass = data ['newpass']
   res = ''
   if current_user.is_authenticated:
      if bcrypt.check_password_hash(current_user.password, oldpass):
         new_password = bcrypt.generate_password_hash(newpass).decode('utf-8')
         current_user.password = new_password
         db.session.commit()
         res = 'password Changed'
      else :
         res = 'You are ot login with correct user...!'
   return (res)