from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re
from PIL import Image
from io import BytesIO
app = Flask(__name__)
app.secret_key = "fazubazu123"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Fazeel@1234'
app.config['MYSQL_DB'] = 'teacher'
mysql = MySQL(app)


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData


@app.route('/')
def allusers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faculty')
    accounts = cursor.fetchall()
    return render_template('allusers.html', accounts=accounts)


@app.route('/myflaskproject/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM faculty WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)
# http://localhost:5000/python/logout - this will be the logout page


@app.route('/myflaskproject/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))
# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests


@app.route('/myflaskproject/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'department' in request.form and 'contact' in request.form and 'image' in request.files:
        # Create variables for easy access
        username = request.form['username'].upper()
        password = request.form['password']
        email = request.form['email']
        department = request.form['department'].upper()
        contact = request.form['contact']
        # Retrieve the image file from the form
        img_file = request.files['image']
        # Convert the image file to bytes
        img_bytes = img_file.read()
        # Convert the image bytes to a PIL image object
        img = Image.open(BytesIO(img_bytes))
        # Convert the PIL image to a bytes object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_bytes = img_byte_arr.getvalue()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM faculty WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            sql = "INSERT INTO faculty (username, password, email, department, contact, image, status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            data = (username, password, email, department, contact, img_bytes, 'Present')
            cursor.execute(sql, data)
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)
# @app.route('/myflaskproject/home')
# def home():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         return render_template('allusers.html', username=session['username'])
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))


@app.route('/myflaskproject/home')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faculty')
    accounts = cursor.fetchall()
    return render_template('allusers.html', accounts=accounts)

@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
      name=request.form['name']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute("SELECT * FROM faculty WHERE username LIKE %s", (name + '%',))
      accounts = cursor.fetchall()
      return render_template('searchedfaculty.html',accounts=accounts)
    return render_template('search.html')
@app.route('/myflaskproject/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM faculty WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/update_column', methods=['POST'])
def update_column():
    new_value = request.form.get('new_value')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE faculty SET status =%s WHERE id =%s',
                   (new_value, session['id']))
    mysql.connection.commit()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM faculty')
    accounts = cursor.fetchall()
    return render_template('allusers.html', accounts=accounts)
