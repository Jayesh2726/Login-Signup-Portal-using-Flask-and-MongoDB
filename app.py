from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv() 

app = Flask(__name__)

app.secret_key = 'jayesh123'

#Mongodb connection

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/user")
client = MongoClient(MONGO_URI)
db = client.get_default_database()
users = db.SignUp

# Home
@app.route('/')
def index():
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    return redirect(url_for('login'))

# signup

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        if not name or not email or not password:
            flash("Fill all Attribute","Error")
            return redirect(url_for('signup'))
        
        if users.find_one({"email":email}):
            flash("This Email Already in USE","Error")
            return redirect(url_for('signup'))
        
        hashed = generate_password_hash(password)
        user_doc = {"name":name,"email":email,"password":hashed}
        users.insert_one(user_doc)

        flash("Signup Successfully", "Success")
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        user = users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            # session मध्ये user info ठेवा (जास्त माहिती न ठेवल्याने सुरक्षित)
            session['user'] = {"id": str(user['_id']), "name": user.get('name'), "email": user.get('email')}
            flash("Login successful", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    # Clear the session first
    session.clear()
    # Show logout success message only
    flash('Logout successful!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)