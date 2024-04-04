from flask import Flask, request, render_template, redirect, session
from flask_bcrypt import Bcrypt

from modules.mailsend import OTP_send
from modules.runquery import runQuery

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret_key'

global glb_info, glb_otp
glb_info,glb_otp = None,None

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/create_database', methods=['GET','POST'])
def register():
    
    global glb_info, glb_otp 

    if(request.method == "POST"):
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        database = request.form['database']

        query = f"SELECT * FROM user_database_list WHERE username = '{username}' AND database_name = '{database}';"
        user_database = runQuery(query=query)

        if(user_database != []):
            return render_template('create_database.html', error = "username-database combination already exists")
        
        if(not username.isalnum() or not database.isalnum() or not username[0].isalpha()):
            return render_template('create_database.html', error = "only use alpha-numeric in username (first must be character) and database name")


        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        glb_info = {
            'username' : username,
            'hashed_password' : hashed_password,
            'email' : email,
            'database' : database
        }

        print(glb_info)
        glb_otp = OTP_send(email=email, random=True)
        return redirect('/create_database/otp')
    

    return render_template('create_database.html')

@app.route('/create_database/otp', methods=['GET','POST'])
def otp_verification():
    if(request.method == 'POST'):
        otp_form = request.form['otp']

        if(not glb_otp or glb_otp != int(otp_form)):
            return render_template('create_database.html', error = "OTP not matched")
        
        query = f'''INSERT INTO user_database_list VALUES ('{glb_info['username']}', 
                                                            '{glb_info['hashed_password']}', 
                                                            '{glb_info['email']}', 
                                                            '{glb_info['database']}'
                                                            );'''
        runQuery(query=query)

        runQuery(query=f"CREATE DATABASE {glb_info['username']}_{glb_info['database']};")
        return redirect('/')

    return render_template('otp_verification.html')

@app.route('/enter_database',methods=['GET','POST'])
def login():
    # When submitting enter_database form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = request.form['database']

        query = f"SELECT * FROM user_database_list WHERE username = '{username}' AND database_name = '{database}';"
        user_database = runQuery(query=query)

        if (user_database == []):
            return render_template('enter_database.html', error='Invalid combination of username and database')
        
        
        if user_database and bcrypt.check_password_hash(user_database[0][1],password):
            session['database'] = user_database[0][0]
            return redirect('/')
        else:
            return render_template('enter_database.html', error='Wrong password')
        
    
    # Normally
    return render_template('enter_database.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')




if __name__ == '__main__':
    app.run(debug=True)
