from flask import Flask, request, render_template, redirect, session
from flask_bcrypt import Bcrypt

from modules.mailsend import OTP_send
from modules.runquery import runQuery
from modules.models import User

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'secret_key'
databases = ''

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
        
        if (userinfo == []):
            return render_template('login.html', error='Invalid username')
        
        
        if userinfo and bcrypt.check_password_hash(userinfo[0][1],password):
            session['username'] = userinfo[0][0]
            print("io")
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Wrong password')
        
    return render_template('login.html')
    

@app.route('/dashboard')
def dashboard():
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

        return render_template('user_dashboard.html', databases = list_databases, user = Current_User)
        
    return redirect('/login')

@app.route('/view_database', methods = ['GET','POST'])
def view_database():    
    # global databases
    if session.get('username'):
        if request.method == 'POST':
            database_id = request.form.get('db')  # Retrieve 'db' from the form data
            if database_id is None:
                # Handle the case when 'db' is not found in the form data
                return "Error: 'db' parameter not found in the form data"
            session['dbname'] = session['username'] + "_" + database_id
            print(database_id)
            print("Mera database id")
            # database_name = session['username']+database_id
            user_databases = runQuery(query=f"SELECT database_name FROM  user_database_list WHERE username = '{session['username']}'")
            user_info = runQuery(query=f"SELECT DISTINCT username,email FROM  user_database_list WHERE username = '{session['username']}'")[0]
            list_databases = []
            
            Current_User = User(user_info)
            # img = "../static/multimedia/abir_newdb/s1.png"
            return render_template('view_database.html', databases = list_databases, user = Current_User, database = database_id)
    
    return redirect('/login')



@app.route('/view_database/create_table', methods=['GET', 'POST'])
def create_table():
    if session.get('username'):
        if session.get('dbname'):
            if request.method == 'POST':
                table_name = request.form.get('table_name')  # Retrieve 'eid' from the form data
                num_attributes = int(request.form.get('num_attributes'))  # Retrieve number of attributes
                user_info = runQuery(query=f"SELECT DISTINCT username,email FROM  user_database_list WHERE username = '{session['username']}'")[0]
                Current_User = User(user_info)
                if not table_name:
                    return "Error: 'eid' parameter not found in the form data"
                type = {"text":"VARCHAR(1024)", "time" : "TIME", "date": "DATE", "image" : "VARCHAR(1024)", "integer" : "INT"}
                # Construct the SQL query to create the table
                columns = []
                for i in range(1, num_attributes + 1):
                    print(request.form.get('attribute' + str(i)))
                    attribute_name = request.form.get('attribute' + str(i))  # Get attribute name
                    print(request.form.get('attribute_type_' + str(i)))
                    attribute_type = type[request.form.get('attribute_type_' + str(i))]  # Get attribute type
                    columns.append(f" {attribute_name} {attribute_type} ")

                # Join the columns into a comma-separated string
                columns_str = ', '.join(columns)

                # Construct the CREATE TABLE query
                create_table_query = f"CREATE TABLE {table_name} ({columns_str});"
                print(create_table_query)
                # Run the query using runQuery function

                return render_template('view_database.html', user = Current_User, database_name = session['dbname'], )
                # Return the result or render a template with the result
                # return "Table created successfully" if result else "Error creating table"


        return redirect('/dashboard')

    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('database', None)
    return redirect('/login')




if __name__ == '__main__':
    app.run(debug=True)
