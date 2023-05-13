import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import redirect
from flask import render_template
from flask import url_for
from flask import flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask_login import login_user
from flask_login import login_required, current_user,login_required, logout_user
import psycopg2
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import schedule
import time

sender_email = 'ticketshownow@gmail.com'
email_password = 'frprtksngzetxfym'


def get_db_connection():
    conn = psycopg2.connect(host='127.0.0.1',
                            database='ticketshow',
                            user='postgres',
                            password='starlord')
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'


login_manager = LoginManager()
login_manager.login_view = 'user_login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("select * from people where user_id='{}'".format(user_id))

    user=cur.fetchall()[0]  
        
    conn.commit()
    cur.close()
    conn.close()

    if user is not None:
        return People(user[0], user[1], user[2] ,user[3])

# defining models

class People(UserMixin):
    def __init__(self, user_id, username, password, email):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.email=email
    def get_id(self):
        return self.user_id
    


@app.route("/")
def index():
    if request.method=="GET":
        return render_template("index.html")
    
    

@app.route('/user/register', methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template("register.html")
    
    elif request.method=='POST':
        username=request.form['name']
        email=request.form['email']
        password=request.form['password']
       
        password=generate_password_hash(password,method='sha256')

    

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('select user_id,username from people')

        rows=cur.fetchall()
        user_id=0
        for row in rows:
            if user_id<row[0]:
                user_id=int(row[0])


            if (row[1]==username):
                flash("Username already exists.Try by some other username")
                return redirect('/user/register')
        user_id+=1
        cur.execute('INSERT INTO people (user_id,username,password,email)'
                    'VALUES (%s, %s, %s, %s)',
                    ( user_id , username, password, email))
        conn.commit()
        cur.close()
        conn.close()
        receiver_email = email


        message = MIMEMultipart("alternative")
        message["Subject"] = "Confirmation of Your Successful Signup on TicketShow"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        header="Dear {},".format(username)
        
    
        html = """
        <html>
        <body>
            {}<br>
            Congratulations on registering for the immunization program! We are thrilled to have you as a participant in this important effort to protect public health. Here's what you can expect now that you've completed your registration:
<br><br>

            Appointment Scheduling: In the coming days, you will receive information on how to schedule your immunization appointment. We will do our best to accommodate your schedule and location preferences.
<br><br>

            After your immunization, we will follow up with you to ensure that you are feeling well and to answer any questions you may have. We may also ask you to participate in surveys or studies to help us improve our program and better understand the impact of immunizations on public health.
<br><br>

            Thank you for joining us in this important effort to protect our communities against preventable diseases. We look forward to seeing you at your appointment and working together to promote health and wellness for all.<br><br>

            Best regards,<br><br>

            Tikakaran Team.<br>
            </p>
        </body>
        </html>""".format(header)


        # Turn these into plain/html MIMEText objects
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
        )
        return redirect(url_for('user_login'))

      
    
@app.route('/user/login', methods=['GET','POST'])
def user_login():
    if request.method=="GET":
        return render_template("user_login.html")
    
    
    
    elif request.method=='POST':
        username=request.form['name']
        password=request.form['password']
        remember = True if request.form.get('remember') else False

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("select * from people where username='{}'".format(username))

        user=cur.fetchone()
         
        conn.commit()
        cur.close()
        conn.close()

        if not user or not check_password_hash(user[2], password):
            flash('Please check your login details and try again.')
            return redirect('/user/login')       
        login_user(People(user[0], user[1], user[2], user[3] ),remember=remember)
        return redirect(url_for('user_dashboard',user_id=user[0]))

@app.route('/user/dashboard',methods=['GET','POST','PUT'])
@login_required
def user_dashboard():
    if request.method=='GET':
        user_id=current_user.user_id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("select * from people where user_id='{}'".format(user_id))
        user=cur.fetchall()[0] 

        cur.execute("select * from personal_details where pd_user_id='{}'".format(user_id))
        child=cur.fetchall()
        if len(child)==0:
            return render_template('user_dashboard_wo_details.html',user=user)


         
        conn.commit()
        cur.close()
        conn.close()
        print("This line is child line",child)


        return render_template("user_dashboard.html",user=user,child=child)    


@app.route('/user/personal_details',methods=['GET','POST'])
@login_required
def personal_details():
    if request.method=='GET':
        user_id=current_user.user_id

        conn = get_db_connection()
        cur = conn.cursor()

        



        cur.execute("select * from people where user_id='{}'".format(user_id))
        
        user=cur.fetchone()
        print(user)
        # print('length of user_list',len(user))
        


        
       
        cur.execute("select * from personal_details where pd_user_id='{}'".format(user_id))
        child=cur.fetchall()
        
        # print(child)
        # print(len(child))
        if len(child)==0:
            return render_template('personal_detail.html',user=user)


        # print(user[0][0])
        print(child)
         
        conn.commit()
        cur.close()
        conn.close()



        return render_template("personal_details.html",user=user,child=child)
    
    elif request.method=='POST':
        user_id=current_user.user_id

        child_name=request.form['child_name']
        dob=request.form['dob']
        father_name=request.form['father_name']
        mother_name=request.form['mother_name']
        blood=request.form['blood']
        feedback=request.form['feedback']
      



        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('select pd_user_id from personal_details')

        rows=cur.fetchall()


        print(rows)
        
        
        cur.execute('INSERT INTO personal_details (pd_user_id, child_name, dob, father_name, mother_name, blood, feedback) '
                    'VALUES ( %s, %s,%s,%s,%s,%s,%s)',
                    (user_id, child_name, dob, father_name, mother_name, blood,feedback))

           
       
        conn.commit()
        cur.close()
        conn.close()

        # # here i schedule all the emails
        # r_mail='devanshushakya27@gmail.com'
        # send_email(r_mail)

        # # Schedule the email to be sent every day at a specific time
        # schedule.every().day.at('20:30').do(send_email)

        # # Continuously run the scheduler
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)


        return redirect(url_for('user_dashboard',user_id=user_id))
    
# def send_email(r_mail):
#     # SMTP server configuration
#     smtp_server = 'smtp.gmail.com'
#     smtp_port = 587 
#     sender_email = 'ticketshownow@gmail.com'
#     sender_password = 'frprtksngzetxfym'
#     receiver_email = r_mail

#     # Email content
#     subject = 'Scheduled Email'
#     body = 'This is a scheduled email.'

#     # Construct the email message
#     message = f'Subject: {subject}\n\n{body}'

#     # Send the email
#     try:
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, receiver_email, message)
#         print('Email sent successfully!')
#     except Exception as e:
#         print('An error occurred while sending the email:', str(e))



        
@app.route('/user/info',methods=['GET'])
def info():
    if request.method=='GET':
        return render_template("info.html")
    





@app.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/forget_password',methods=['GET','POST'])
def forget_password():
    if request.method=="GET":
        return render_template("forget_password.html")
    





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


