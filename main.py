from flask import Flask, render_template, request, redirect, session, flash, jsonify
from mysqlconnection import MySQLConnector
import re
import hashlib as hl
import aiml
import os
import pyttsx3

engine1=pyttsx3.init()


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[0-9]')
PASS_REGEX = re.compile(r'.*[0-9]')

app = Flask(__name__)
app.secret_key = "ThisIsSecretadfasdfasdf!"

mysql = MySQLConnector(app,'login_reg')

@app.route('/')
def index():
    
    
    print(session)

    #engine1.setProperty('rate', 4)
    #engine1.say("welcome to ChatterBot Application")
    #engine1.runAndWait()
    
    return render_template('index.html')

   
    
@app.route('/about')
def about():
    print(session)
    return render_template('about.html')

@app.route('/services')
def services():
    print(session)
    return render_template('services.html')

@app.route('/contact')
def contact():
    print(session)
    return render_template('contact.html')

@app.route('/success1')
def success1():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():
	message = str(request.form['messageText'])

	kernel = aiml.Kernel()

	if os.path.isfile("bot_brain.brn"):
	    kernel.bootstrap(brainFile = "bot_brain.brn")
	else:
	    kernel.bootstrap(learnFiles = os.path.abspath("aiml/std-startup.xml"), commands = "load aiml b")
	    kernel.saveBrain("bot_brain.brn")

	
	while True:
	    if message == "quit":
	        exit()
	    elif message == "save":
	        kernel.saveBrain("bot_brain.brn")
	    else:
	        bot_response = kernel.respond(message)
	        engine1.setProperty('rate', 100)
	        engine1.say(bot_response)
	        engine1.runAndWait()
	        print (bot_response)
	        return jsonify({'status':'OK','answer':bot_response})
	    
@app.route('/register', methods=['POST'])
def register_user():
    print("in register")
    flag=0
    msg=""
    input_email = request.form['email']
    email_query = "SELECT * FROM users WHERE email = :email_id"
    query_data = {'email_id': input_email}
    stored_email = mysql.query_db(email_query, query_data)


    print(request.form)
    print(request.form['email'])
    print(session)

    for x in request.form:
        if len(request.form[x]) < 1:
            flag=1
            print (x + " cannot be blank!", 'blank')
    

    if NAME_REGEX.search(request.form['first_name']):
        flag=1
        msg="First name cannot contain any numbers"
        print ("First name cannot contain any numbers", 'error')
    if NAME_REGEX.search(request.form['last_name']):
        flag=1
        msg="Last name cannot contain any numbers"
        print ("Last name cannot contain any numbers", 'error')

    if len(request.form['password']) < 6:
        flag=1
        msg="Password must be more than 6 characters"
        print ("Password must be more than 8 characters", 'password')

    if not EMAIL_REGEX.match(request.form['email']):
        flag=1
        msg="Email must be a valid email"
        print ("Email must be a valid email", 'error')
        print ("Email must be a valid email")
    
    if not PASS_REGEX.search(request.form['password']):
        flag=1
        msg="Password must have a number and an uppercase letter"
        print ("Password must have a number and an uppercase letter", 'password')
        print ("Password must have a number and an uppercase letter")
    if request.form['password'] != request.form['confirm_password']:
        flag=1
        msg="Password and Password Confirmation should match"
        print ("Password and Password Confirmation should match", 'password')
        
    if stored_email:
        flag=1
        msg="Email already exists!"
        print ("Email already exists!")


    if flag==1:
        print ("error")
        #return redirect('/')
        return render_template('index.html',status1=msg)
    else:
        print ("All Good!!!!", 'good')
        query = "INSERT INTO users (f_name, l_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email_id, :pass, NOW(), NOW())"
        
        data = {
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email_id': request.form['email'],
                'pass': request.form['password']
            }
        
        mysql.query_db(query, data)

        input_email = request.form['email']
        email_query = "SELECT * FROM users WHERE email = :email_id"
        query_data = {'email_id': input_email}
        stored_email = mysql.query_db(email_query, query_data)

        session['user_id'] = stored_email[0]['id']
         
        print ("This email address you entered " + input_email + " is a valid email address. Thank you!")
        return redirect('/')
        #return render_template('services.html')


    
@app.route('/success')
def success():
    print (session)
    return redirect('/success1')

@app.route('/login', methods=['POST'])
def login():

    input_email = request.form['email']
    input_password = request.form['password']
    email_query = "SELECT * FROM users WHERE email = :email_id"
    query_data = {'email_id': input_email}
    stored_email = mysql.query_db(email_query, query_data)

    if not EMAIL_REGEX.match(request.form['email']):
        print ("Email must be a valid email", 'error')

    if not stored_email:
        print("User does not exist!")
        return redirect('/')

    else:
        if request.form['password'] == stored_email[0]['password']:
            session['user_id'] = stored_email[0]['id']
            return redirect('/success')
        else:
            print ("Wrong password, try again!")
            return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)