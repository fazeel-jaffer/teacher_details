from flask import Flask, render_template, request, redirect, url_for, session, make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import mysql.connector
import re
from PIL import Image
import pybase64
import logging
import smtplib
from email.message import EmailMessage
app = Flask(__name__)
app.secret_key = "fazubazu123"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Fazeel@1234'
app.config['MYSQL_DB'] = 'teacher'
mysql = MySQL(app)


@app.route('/')
def allusers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT * FROM faculty')
    # accounts = cursor.fetchall()
    # return render_template('allusers.html', accounts=accounts)
    cursor.execute(
        'SELECT id, username,password,email,department,contact,image, status FROM faculty')
    users = cursor.fetchall()
    # create a list of dictionaries with the user data and image URL
    user_data = []
    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['username'] = user['username']
        user_dict['email'] = user['email']
        user_dict['contact'] = user['contact']
        user_dict['department'] = user['department']
        user_dict['status'] = user['status']
        user_dict['image_url'] = '/display_image/{}'.format(user['id'])
        user_data.append(user_dict)
        # render the allusers.html template with the user data
    return render_template('allusers.html', accounts=user_data)

# @app.route('/display_image/<int:user_id>')
# def display_image(user_id):
#     # Fetch the image data from the database using the user ID
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT image FROM faculty WHERE id = %s", (user_id,))
#     row = cur.fetchone()
#     if row and row[0]:
#         image_data = row[0]
#         # Create a response object with the image data and content type
#         response = make_response(image_data)
#         response.headers.set('Content-Type', 'image/png')
#     else:
#         response = make_response("Image not found")
#         response.headers.set('Content-Type', 'text/plain')
#     return response


@app.route('/display_image/<int:user_id>')
def display_image(user_id):
    try:
        # Fetch the image data from the database using the user ID
        cur = mysql.connection.cursor()
        cur.execute("SELECT image FROM faculty WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if row and row[0]:
            # Decode the base64-encoded image data
            image_data = pybase64.b64decode(row[0])
            # Create a response object with the image data and content type
            response = make_response(image_data)
            response.headers.set('Content-Type', 'image/png')
        else:
            response = make_response("Image not found")
            response.headers.set('Content-Type', 'text/plain')
        return response
    except Exception as e:
        logging.error(
            'Error displaying image for user ID {}: {}'.format(user_id, e))
        response = make_response("Error displaying image")
        response.headers.set('Content-Type', 'text/plain')
        return response


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
        image = request.files['image']
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
            temp_file = 'temp.png'
            with Image.open(image) as img:
                img.thumbnail((280, 280))
                img = img.convert('RGB')  # convert to RGB mode
                img.save(temp_file, 'PNG')
            sql = "INSERT INTO faculty (username, password, email, department, contact, image, status) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            data = (username, password, email,
                    department, contact, '', 'Present')
            cursor.execute(sql, data)
            user_id = cursor.lastrowid
            with open(temp_file, 'rb') as f:
                img_data = f.read()
                encoded_data = pybase64.b64encode(img_data)
                update_stmt = "UPDATE faculty SET image=%s WHERE id=%s"
            cursor.execute(update_stmt, (encoded_data, user_id))
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
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT * FROM faculty')
    # accounts = cursor.fetchall()
    # return render_template('allusers.html', accounts=accounts)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT * FROM faculty')
    # accounts = cursor.fetchall()
    # return render_template('allusers.html', accounts=accounts)
    cursor.execute(
        'SELECT id, username,password,email,department,contact,image, status FROM faculty')
    users = cursor.fetchall()
    # create a list of dictionaries with the user data and image URL
    user_data = []
    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['username'] = user['username']
        user_dict['email'] = user['email']
        user_dict['contact'] = user['contact']
        user_dict['department'] = user['department']
        user_dict['status'] = user['status']
        user_dict['image_url'] = '/display_image/{}'.format(user['id'])
        user_data.append(user_dict)
        # render the allusers.html template with the user data
    return render_template('allusers.html', accounts=user_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        name = request.form['name']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM faculty WHERE username LIKE %s", ('%' + name + '%',))
        accounts = cursor.fetchall()
        user_data = []
        for user in accounts:
            user_dict = {}
            user_dict['id'] = user['id']
            user_dict['username'] = user['username']
            user_dict['email'] = user['email']
            user_dict['contact'] = user['contact']
            user_dict['department'] = user['department']
            user_dict['status'] = user['status']
            user_dict['image_url'] = '/display_image/{}'.format(user['id'])
            user_data.append(user_dict)
        return render_template('searchedfaculty.html', accounts=user_data)
    return render_template('search.html')


@app.route('/myflaskproject/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM faculty WHERE id = %s', (session['id'],))
        # account = cursor.fetchone()
        # # Show the profile page with account info
        # return render_template('profile.html', account=account)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM faculty')
        # accounts = cursor.fetchall()
        # return render_template('allusers.html', accounts=accounts)
        cursor.execute('SELECT * FROM faculty WHERE id=%s', (session['id'],))
        users = cursor.fetchone()
    # create a list of dictionaries with the user data and image URL
        user_data = []
        user_dict = {}
        user_dict['id'] = users['id']
        user_dict['username'] = users['username']
        user_dict['email'] = users['email']
        user_dict['contact'] = users['contact']
        user_dict['department'] = users['department']
        user_dict['image_url'] = '/display_image/{}'.format(users['id'])
        user_data.append(user_dict)
        # render the allusers.html template with the user data
        return render_template('profile.html', account=user_dict)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/update_column', methods=['POST'])
def update_column():
    new_value = request.form.get('new_value')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE faculty SET status =%s WHERE id =%s',
                   (new_value, session['id']))
    mysql.connection.commit()
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute('SELECT * FROM faculty')
    # accounts = cursor.fetchall()
    # return render_template('allusers.html', accounts=accounts)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        'SELECT id, username,password,email,department,contact,image, status FROM faculty')
    users = cursor.fetchall()
    # create a list of dictionaries with the user data and image URL
    user_data = []
    for user in users:
        user_dict = {}
        user_dict['id'] = user['id']
        user_dict['username'] = user['username']
        user_dict['email'] = user['email']
        user_dict['contact'] = user['contact']
        user_dict['department'] = user['department']
        user_dict['status'] = user['status']
        user_dict['image_url'] = '/display_image/{}'.format(user['id'])
        user_data.append(user_dict)
        # render the allusers.html template with the user data
    return render_template('allusers.html', accounts=user_data)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Compose the email
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = f'New message from {name}'
        msg['From'] = email
        msg['To'] = 'demo@gmail.com'

        # Send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('', '')
        server.send_message(msg)
        server.quit()

        return 'Thank you for your message!'

    return render_template('contact.html')
