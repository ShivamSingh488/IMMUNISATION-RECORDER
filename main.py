import smtplib
import os
import psycopg2
from datetime import datetime, timedelta
import calendar
from datetime import date


os.chdir(r"D:\someauto")
# os.mkdir("testing")


sender_email = 'ticketshownow@gmail.com'
email_password = 'frprtksngzetxfym'

def get_db_connection():
    conn = psycopg2.connect(host='127.0.0.1',
                            database='ticketshow',
                            user='postgres',
                            password='starlord')
    return conn

def add_weeks_or_months(date_str, weeks=0, months=0):
    date = datetime.strptime(date_str, "%Y-%m-%d")

    # Adding weeks
    delta = timedelta(weeks=weeks)
    result = date + delta

    # Adding months
    if months != 0:
        year = result.year + (result.month + months - 1) // 12
        month = (result.month + months - 1) % 12 + 1
        day = min(result.day, calendar.monthrange(year, month)[1])
        result = result.replace(year=year, month=month, day=day)

    return result.strftime("%Y-%m-%d")

def send_email(r_email):
    # SMTP server configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'ticketshownow@gmail.com'
    sender_password = 'frprtksngzetxfym'
    receiver_email = r_email

    # Email content

    subject = 'Get your child vaccinated today'

    
    body ="""
    Dear Parent,
    \n\nThis is a reminder to get your child vaccinated today. Vaccinations are an important part of maintaining your child's health and protecting them from preventable diseases.
    \nPlease schedule an appointment with your healthcare provider or visit a vaccination center to ensure that your child's immunizations are up to date.
    \nThank you for prioritizing your child's well-being.
    \nBest regards,
    \nYour Healthcare Team
\n\nCheck out website to have more information at http://127.0.0.1:5000/user/info"""

    # Construct the email message
    message = f'Subject: {subject}\n\n{body}'

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        print('Email sent successfully!')
    except Exception as e:
        print('An error occurred while sending the email:', str(e))

# Call the send_email function
if __name__=="__main__":
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('select * from personal_details')
    rows=cur.fetchall()

    cur.execute('select * from people')
    people=cur.fetchall()



    conn.commit()
    cur.close()
    conn.close()
    # print("people are",people)

    results={}
    dobs={}
    for i in range(len(rows)):
        results[rows[i][0]]=[]
        dobs[rows[i][0]]=[]

    # print(results)
    # print(dobs)
    for row in rows:
        dobs[row[0]].append(people[i][3])
        
        # print(row)

        date_str=str(row[2])
        

        # print(row[2])
        result0=row[2]
        results[row[0]].append(result0)
        # print(result0)


        result1 = add_weeks_or_months(date_str, weeks=6)
        results[row[0]].append(result1)
        # print(result1)  # Output: 2023-06-22

        result2 = add_weeks_or_months(date_str, weeks=10)
        results[row[0]].append(result2)
        # print(result2)  # Output: 2023-08-03

        result3 = add_weeks_or_months(date_str, weeks=12)
        results[row[0]].append(result3)
        # print(result3)  # Output: 2023-08-17

        result4 = add_weeks_or_months(date_str, months=14)
        results[row[0]].append(result4)
        # print(result4)  # Output: 2023-08-11

        result5 = add_weeks_or_months(date_str, months=18)
        results[row[0]].append(result5)
        # print(result5)  # Output: 2023-08-11

        # print("\n")
    # print(results)


    today = date.today()
    formatted_date = today.strftime("%Y-%m-%d")
    # print(formatted_date)

    # print(results)
    # print(rows) 
    # print("dob is ",dobs)

    for key in results:
        # print(key)
        for i in results[key]:
            # print(i)
            if str(i) == str(formatted_date):
                print("The key is ",key)
                # if 
                # print(dobs[key][0])
                r_email=dobs[key][0]

                
                send_email(r_email)






        



        



   
  
     
