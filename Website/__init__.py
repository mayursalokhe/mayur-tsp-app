from flask import Flask, Blueprint, request, redirect, render_template,flash, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_admin import Admin
from flask import abort,session
from flask_login import UserMixin,current_user
from flask_admin.contrib.sqla import ModelView
from datetime import timedelta
import sqlite3
import pickle

#Creating app and database
db = SQLAlchemy()
DB_NAME = "database2.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mayur key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=60)

    db.init_app(app)

    admin = Admin(app)
    admin.add_view(AdminModel(Contact,db.session))
    admin.add_view(AdminModel(Data,db.session))

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')

    create_database(app)
    return app

class Contact(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120),unique=True)
    message = db.Column(db.String(200))

class Data(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80))
    pclass = db.Column(db.Integer)
    age = db.Column(db.Integer)
    fare = db.Column(db.Integer)
    sib = db.Column(db.Integer)
    sp = db.Column(db.Integer)
    par = db.Column(db.Integer)
    child = db.Column(db.Integer)
    sex = db.Column(db.Integer)
    embarked = db.Column(db.Integer)

class AdminModel(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)

def create_database(app):
    if not path.exists('Website/static'+ DB_NAME):
        db.create_all(app=app)

#auth section
auth = Blueprint('auth',__name__)

@auth.route('/adminlogin',methods = ['GET','POST'])
def adminlogin():
    if request.method == "POST":
        if request.form.get('email') == 'mayursalokhe9201@gmail.com' and request.form.get('password') == 'adminmayur':
            session['logged_in'] = True
            return redirect('/admin')
        else:
            flash('Invalid Details!!',category='error')
    return render_template("adminlogin.html",user=current_user)

@auth.route('/contact',methods=['GET','POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        user = Contact.query.filter_by(email=email).first()

        if user:
            flash('User already exists.')
        elif len(email) < 4:
            flash('Email ID must be greater than 4 characters.')
        elif len(name) < 2:
            flash('Username must be grater than 1 character.', category='error')
        else:
            new_user = Contact(username=name, email=email,message=message)

            db.session.add(new_user)
            db.session.commit()
            flash('Message Submited', category='success')
            return redirect(url_for("views.contact"))
    return render_template("contact.html",user=current_user)

#viwes section
views = Blueprint('views', __name__)

# rendering all templates here
@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html", user=current_user)


@views.route('/index')
def index():
    return render_template("index.html", user=current_user)


@views.route('/index2')
def index2():
    return render_template("index2.html", user=current_user)


@views.route('/about')
def about():
    return render_template("about.html", user=current_user)


@views.route('/contact')
def contact():
    return render_template("contact.html", user=current_user)


# Admin Section
@views.route('/adminlogin')
def adminlogin():
    return render_template("adminlogin.html", user=current_user)


# Prediction Section
model = pickle.load(open('Website/static/model.pkl','rb'))


@views.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    user_name = request.form['Name']
    pclass = request.form['Pclass']
    age = request.form['Age']
    fare = request.form['Fare']
    sp = request.form['spouse']
    sib = request.form['sib']
    par = request.form['par']
    child = request.form['child']
    sibsp = sib + sp
    parch = par + child
    sex = request.form['Sex']
    embarked = request.form['Embarked']
    int_features = [[pclass, sex, age, sibsp, parch, fare, embarked]]
    prediction = model.predict(int_features)
    probability_user = model.predict_proba(int_features)
    predict_prob = probability_user[0][1] * 100
    if prediction == 0:
        output = "Oh no! " + user_name + " You didn't make it"
    else:
        output = "Nice! " + user_name + " You survived"

    conn = sqlite3.connect('Website/static/database2.db')
    conn.execute(
        'CREATE TABLE IF NOT EXISTS Data (id INTEGER PRIMARY KEY, username STRING, pclass INTEGER, age INTEGER, '
        'fare INTEGER, par INTEGER, child INTEGER, sib INTEGER, sp INTEGER, embarked INTEGER, sex INTEGER)')
    conn.close()

    dataset = Data(username=user_name,pclass=pclass, age=age, fare=fare, sib=sib, sp=sp, embarked=embarked, child=child, par=par, sex=sex)
    db.session.add(dataset)
    db.session.commit()

    return render_template('index.html', prediction_text='{}'.format(output), name=user_name,
                           probability='Chances you survive {} %'.format(predict_prob), user=current_user)
