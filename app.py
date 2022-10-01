from crypt import methods
from email.policy import default
from enum import unique
from flask import Flask, render_template, flash, request, make_response, redirect, url_for, Response
from forms import ConnectForm, UserForm, PasswordForm, PostForm, LoginForm, SearchForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
#import git
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import requests


app = Flask(__name__)
# add CKeditor
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'mysuperkey'
#add DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
UPLOAD_FOLDER = 'static/imgs/users/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#flask login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#create model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    pet_name = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    #password stuff
    password_hash = db.Column(db.String(128))
    # user can have many posts
    posts = db.relationship('Posts', backref='post_auth')

    @property
    def passwrod(self):
        raise AttributeError('Password is not a readable attribute')
    @passwrod.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #create A string
    def __repr__(self):
        return '<Name %r>' % self.name

#to create the db run in python shell: from app import db -> db.create_all()

# Create blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign key to link users (refer to primary key of the user)
    post_auth_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# update from github
#@app.route('/git_update', methods=['POST'])
#def git_update():
#    repo = git.Repo('./flask_my_blog')
#    origin = repo.remotes.origin
#    repo.create_head('main',
#                     origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
#    origin.pull()
#    return '', 200

def send(text):
    token = os.environ['TOKEN']
    chat_id = os.environ['ID']
    url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text
    results = requests.get(url_req)
    print(results.json())

@app.route('/')
def index():
    posts = Posts.query
    #grab linux posts from database
    posts = posts.filter(Posts.slug.like('main'))
    posts = posts.order_by(Posts.title).all()
    return render_template("index.html", posts=posts)

# carousel
@app.route('/carousel')
def carousel():
    return render_template("carousel.html")
# end carousel

# add users
@app.route('/add/users', methods=['GET', 'POST'])
def add_users():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            #Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username=form.username.data.lower(), name=form.name.data, email=form.email.data, pet_name=form.pet_name.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        send(str(form.email.data) + ' Register to website')
        name = form.name.data
        form.name.date = ''
        form.username.data = ''
        form.email.data = ''
        form.password_hash.data = ''
        form.password_hash2.data = ''
        flash("User added successfully!")
        return redirect(url_for('login'))
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_users.html", form=form, name=name, our_users=our_users)

# update user
@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        name_to_update.password_hash = hashed_pw
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template("update_user.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error!")
            return render_template("update_user.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update_user.html", form=form, name_to_update=name_to_update, id=id)


# delete user
@app.route('/delete-user/<int:id>')
@login_required
def delete_user(id):
    if id == current_user.id or current_user.pet_name == "admin":
        name = None
        form = UserForm()
        user_to_delete = Users.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("User deleted successfully!")
            our_users = Users.query.order_by(Users.date_added)
            if current_user.pet_name == "admin":
                return render_template("admin.html", form=form, name=name, our_users=our_users)
            else:
                logout_user()
                return render_template("index.html", form=form, name=name, our_users=our_users)
        except:
            flash("There was a problem!")
            return render_template("index.html", form=form, name=name, our_users=our_users)
    else:
        flash("Can't delete!")
        return redirect(url_for('index'))


# create login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data.lower()).first()
        if user:
            #check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login succesfull!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password - try again!')
        else:
            flash("This user doesn't exist!")
    return render_template('login.html', form=form)

# create logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!")
    return redirect(url_for('index'))

# create dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    pic = current_user.profile_pic
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.profile_pic = request.files['profile_pic']
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        name_to_update.password_hash = hashed_pw
        # check fot profile pic
        if request.files['profile_pic']:
            # Grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save that image
            saver = name_to_update.profile_pic
            #change it to a string to save to db
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User updated successfully!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
            except:
                flash("Error!")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)
        else:
            name_to_update.profile_pic = pic
            db.session.commit()
            flash("User updated successfully!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)     
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update, id=id)

    return render_template('dashboard.html')

# Create add-post page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post_auth = current_user.id
        post = Posts(title = form.title.data, content = form.content.data, post_auth_id = post_auth, slug = form.slug.data)
        send(str(form.title.data) + ' post added to ' + str(form.slug.data))
        # clear the forms
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # add post data to database
        db.session.add(post)
        db.session.commit()
        # return a massege
        flash("Blog Post added successfully!")
    # Redirect to the webpage
    return render_template('add_post.html', form=form)

# show posts page
@app.route('/posts')
@login_required
def posts():
    #grab all posts from database
    posts = Posts.query
    posts = posts.filter(or_(Posts.slug.like('Linux'), Posts.slug.like('Docker'), Posts.slug.like('Jenkins'),
                         Posts.slug.like('Git'), Posts.slug.like('Rancher'), Posts.slug.like('Kubernetes'),
                          Posts.slug.like('Raspberry-pi'), Posts.slug.like('Arduino')))
    posts = posts.order_by(Posts.date_posted).all()
    return render_template('posts.html', posts=posts)

#TOPIC_CHOICES = [('linux', 'Linux'), ('docker', 'Docker'), ('jenkins', 'Jenkins'), ('git', 'Git'), ('rancher', 'Rancher'), ('kubernetes', 'Kubernetes')]

@app.route('/linux-posts')
@login_required
def Linux_posts():
    posts = Posts.query
    #grab linux posts from database
    posts = posts.filter(Posts.slug.like('Linux'))
    posts = posts.order_by(Posts.title).all()
    return render_template('linux_posts.html', posts=posts)

@app.route('/docker-posts')
@login_required
def Docker_posts():
    posts = Posts.query
    #grab docker posts from database
    posts = posts.filter(Posts.slug.like('Docker'))
    posts = posts.order_by(Posts.title).all()
    return render_template('docker_posts.html', posts=posts)

@app.route('/jenkins-posts')
@login_required
def Jenkins_posts():
    posts = Posts.query
    #grab jenkins posts from database
    posts = posts.filter(Posts.slug.like('Jenkins'))
    posts = posts.order_by(Posts.title).all()
    return render_template('jenkins_posts.html', posts=posts)

@app.route('/git-posts')
@login_required
def Git_posts():
    posts = Posts.query
    #grab git posts from database
    posts = posts.filter(Posts.slug.like('Git'))
    posts = posts.order_by(Posts.title).all()
    return render_template('git_posts.html', posts=posts)

@app.route('/kubernetes-posts')
@login_required
def Kubernetes_posts():
    posts = Posts.query
    #grab kubernetes posts from database
    posts = posts.filter(Posts.slug.like('Kubernetes'))
    posts = posts.order_by(Posts.title).all()
    return render_template('kubernetes_posts.html', posts=posts)

@app.route('/Python-posts')
@login_required
def Python_posts():
    posts = Posts.query
    #grab kubernetes posts from database
    posts = posts.filter(Posts.slug.like('Python'))
    posts = posts.order_by(Posts.title).all()
    return render_template('python_posts.html', posts=posts)

@app.route('/Raspberry-pi-posts')
@login_required
def Raspberry_pi_posts():
    posts = Posts.query
    #grab kubernetes posts from database
    posts = posts.filter(Posts.slug.like('Raspberry-pi'))
    posts = posts.order_by(Posts.title).all()
    return render_template('raspberry_pi_posts.html', posts=posts)

@app.route('/Arduino-posts')
@login_required
def Arduino_posts():
    posts = Posts.query
    #grab kubernetes posts from database
    posts = posts.filter(Posts.slug.like('Arduino'))
    posts = posts.order_by(Posts.title).all()
    return render_template('arduino_posts.html', posts=posts)

# show specific post page
@app.route('/posts/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

# edit posts
@app.route('/post/edit/<int:id>', methods=['GET', 'POST'] )
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        # update database
        db.session.add(post)
        db.session.commit()
        flash("Post has been updated!!")
        return redirect(url_for('post', id=post.id))
    if current_user.id == post.post_auth_id or current_user.pet_name == "admin":
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You aren't authorized to edit this post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

# delete post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    admin_id = current_user.pet_name
    id = current_user.id
    if admin_id == "admin":
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog post was deleted!!")
            return redirect(url_for('admin'))
        except:
            flash("There was a problem deleting post!")
            posts = Posts.query.order_by(Posts.date_posted)
            return redirect(url_for('admin'))
    elif id == post_to_delete.post_auth_id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog post was deleted!!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash("There was a problem deleting post!")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash("You aren't authorized to delete this post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


@app.route('/video')
def video():
    return render_template("video.html")

# pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# create search function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # get data from submitted form
        post.searched = form.searched.data
        # query the database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template("search.html", form=form, searched=post.searched, posts=posts)

# Create admin area
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    id = current_user.pet_name
    if id == "admin":
        name = None
        #show users
        our_users = Users.query.order_by(Users.date_added)
        #show posts
        posts = Posts.query
        posts = posts.filter(or_(Posts.slug.like('Linux'), Posts.slug.like('Docker'), Posts.slug.like('Jenkins'),
                         Posts.slug.like('Git'), Posts.slug.like('Rancher'), Posts.slug.like('Kubernetes'),
                          Posts.slug.like('Raspberry-pi'), Posts.slug.like('Arduino')))
        posts = posts.order_by(Posts.date_posted).all()        #edit main page
        main_posts = Posts.query
        main_posts = main_posts.filter(Posts.slug.like('main'))
        main_posts = main_posts.order_by(Posts.title).all()
        return render_template("admin.html", our_users=our_users, posts=posts, main_posts=main_posts)
    else:
        flash("You are not Admin user!")
        return redirect(url_for('index'))


# Create add-post page
@app.route('/add-main-posts', methods=['GET', 'POST'])
@login_required
def add_main_post():
    id = current_user.pet_name
    if id == "admin":
        form = PostForm()
        if form.validate_on_submit():
            post_auth = current_user.id
            post = Posts(title = form.title.data, content = form.content.data, post_auth_id = post_auth, slug = "main")
            # clear the forms
            form.title.data = ''
            form.content.data = ''
            form.slug.data = ''
            # add post data to database
            db.session.add(post)
            db.session.commit()
            # return a massege
            flash("Blog Post added successfully!")
            return redirect(url_for('admin'))
        # Redirect to the webpage
        #posts = Posts.query.order_by(Posts.date_posted)
        return render_template('add_main_post.html', form=form)
    else:
        flash("You are not Admin user!")
        return redirect(url_for('index'))


# edit posts
@app.route('/admin-post/edit/<int:id>', methods=['GET', 'POST'] )
@login_required
def edit_post_admin(id):
    main_posts = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        main_posts.title = form.title.data
        main_posts.slug = 'main'
        main_posts.content = form.content.data
        # update database
        db.session.add(main_posts)
        db.session.commit()
        flash("Post has been updated!!")
        return redirect(url_for('admin'))
    if current_user.pet_name == "admin":
        form.title.data = main_posts.title
        form.slug.data = main_posts.slug
        form.content.data = main_posts.content
        return render_template('admin-edit-main-post.html', form=form)
    else:
        flash("You aren't authorized to edit this post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


# update user admin
@app.route('/update-user-admin/<int:id>', methods=['GET', 'POST'])
def update_user_admin(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.pet_name = request.form['pet_name']
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        name_to_update.password_hash = hashed_pw
        try:
            db.session.commit()
            flash("User updated successfully!")
            return redirect(url_for('admin'))
        except:
            flash("Error!")
            return redirect(url_for('index'))
    else:
        return render_template("update_user_admin.html", form=form, name_to_update=name_to_update, id=id)


# Create Custom Error Pages
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404
# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500
# Themes
@app.route("/set")
@app.route("/set/<theme>")
def set_theme(theme="light"):
  res = make_response(redirect(url_for("index")))
  res.set_cookie("theme", theme)
  return res


# send telegram message from users
@app.route('/contact-us', methods=['GET', 'POST'])
def connect_us():
    name = None
    message = None
    form = ConnectForm()
    if form.validate_on_submit():
        auth = current_user.username
        name = str(auth)
        message = form.message.data
        text = name + ':  ' + message
        send(text)
        #clear the form
        form.name.data = ''
        form.message.data = ''
        flash('Send message successfuly!')
        return redirect(url_for('index'))
    return render_template("contact-us.html", name = name, message=message, form = form)