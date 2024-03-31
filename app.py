from flask import Flask, request, render_template, redirect, session
from flask_bcrypt import Bcrypt

from modules.mailsend import OTP_send

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

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        glb_info = {
            'username' : username,
            'hashed_password' : hashed_password,
            'email' : email,
            'database' : database
        }

        print(glb_info)
        return redirect('/')

    return render_template('create_database.html')

if __name__ == '__main__':
    app.run(debug=True)
