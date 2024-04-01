from flask import Flask, request, render_template, redirect, session
from flask_bcrypt import Bcrypt
from runquery import runQuery

from modules.mailsend import OTP_send
from models import User

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret_key'

global glb_info, glb_otp
glb_info,glb_otp = None,None


def check_to_all_users(username, database):
    query = f"SELECT * FROM user_database_list WHERE username = '{username}' AND database_name = '{database}';"
    user = runQuery(query=query)

    if(user != []):
        return 'err'

    return 'ok'


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

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        glb_info = {
            'username' : username,
            'hashed_password' : hashed_password,
            'email' : email,
            'database' : database
        }
        val = check_to_all_users(username, database)
        if val == 'err':
            return render_template('create_database.html', error='Username and database name pair already exists')
        
        runQuery(query = f"INSERT INTO user_database_list VALUES ('{glb_info['username']}','{glb_info['hashed_password']}','{glb_info['email']}','{glb_info['database']}');")
        runQuery(query = f"CREATE DATABASE {glb_info['database']}")
        print(glb_info)
        return redirect('/')

    return render_template('create_database.html')

@app.route('/login', methods=['GET','POST'])
def login():
    # When submitting login form
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        userinfo = runQuery(query=f"SELECT * FROM user_database_list WHERE username = '{username}';")
        for item in userinfo:
            print("mugen train")
            for valus in item:
                print(valus)
        
        if userinfo == []:
            return render_template('login.html', error = 'Username does not exist')
        if userinfo and bcrypt.check_password_hash(userinfo[0][1],password):
            session['username'] = userinfo[0][0]
            return redirect('/dashboard')
        else :
            return render_template('login.html', error = 'Password does not match')
        if session.get('username'):
            print('User logged in')
            return redirect('/dashboard')
    return render_template('login.html')
    

@app.route('/dashboard')
def kgp_student():
    if session.get('username'):

        user_databases = runQuery(query=f"SELECT database_name FROM  user_database_list WHERE username = '{session['username']}'")
        user_info = runQuery(query=f"SELECT DISTINCT username,email FROM  user_database_list WHERE username = '{session['username']}'")[0]
        list_databases = []
        print(user_databases)
        i = 0
        for item in user_databases:
            print(item)
            list_databases.append(item[0])
        Current_User = User(user_info)
        # additional_info = runQuery(query = f'''
        #                                     SELECT roll_no, institute_email
        #                                     FROM kgp_student
        #                                     JOIN all_users ON kgp_student.username = all_users.username
        #                                     WHERE kgp_student.username = '{username}'
        #                                     ''')[0]
        

        # # print(additional_info)
        # Current_User = Kgp_Student(user_info, additional_info)

        # list_events = runQuery(query=f"SELECT * FROM events") # list of events

        # vol_apply_list1 = runQuery(query=f"SELECT event_id FROM volunteers WHERE username='{session['username']}' AND type=1") # list of applied for vol events
        # vol_apply_list = []
        # if vol_apply_list1 is not None:
        #     for item in vol_apply_list1:
        #         vol_apply_list.append(item[0])

        # vol_approve_list1 = runQuery(query=f"SELECT event_id FROM volunteers WHERE username='{session['username']}' AND type=2") # list of approved for vol events
        # vol_approve_list = []
        # if vol_approve_list1 is not None:
        #     for item in vol_approve_list1:
        #         vol_approve_list.append(item[0])

        # partici_list1 = runQuery(query=f"SELECT part_event_id FROM participate WHERE part_user='{session['username']}'") # list of approved for vol events
        # partici_list = []
        # if partici_list1 is not None:
        #     for item in partici_list1:
        #         partici_list.append(item[0])
        
        # disapp = runQuery(query=f"SELECT event_id FROM volunteers WHERE username='{session['username']}' AND type=3") # list of approved for vol eventss
        # disapproved = []
        # if disapp is not None:
        #     for item in disapp:
        #         disapproved.append(item[0])

        return render_template('kgpStudent.html', databases = list_databases, user = Current_User)
        
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
