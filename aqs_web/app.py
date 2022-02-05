from sqlite3 import Cursor
from jinja2 import *
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Length
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from passlib.hash import sha256_crypt
from wtforms import StringField, PasswordField, SubmitField
import hashlib
import urllib
from urllib.parse import unquote
import html

import pyodbc

app = Flask(__name__)
app.static_folder = 'static'
params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=DESKTOP-1QKIK6R\SQLEXPRESS;DATABASE=myerp101;Trusted_Connection=yes;')
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#i dont know how to configure secret key, but it is needed for flask_wtf
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
CORS(app)

#put ur server name here
#desmond: DESKTOP-7REM3J1\SQLEXPRESS
#calvin: DESKTOP-1QKIK6R\SQLEXPRESS
#jingwen: DESKTOP-KNDFRSA
forSQLServerName = 'DESKTOP-1QKIK6R\SQLEXPRESS';

# SALESPERSON FUNCTIONS

# Updates database with edited information for each component
@app.route("/updateComponent", methods=['POST'])
def update_component():
    data = request.get_json()
    print(data)
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE dbo.quotation_component
                SET crawl_info = ?, unit_price = ?
                WHERE component_no = ?
                ''', data["edited_crawl_info"], data["unit_price"], data["component_no"])
    try:
        conn.commit()
        cursor.close()
        return jsonify(data), 201
    except Exception:
        cursor.close()
        return jsonify({
            "code": 404,
            "message": "Unable to commit to database."
        }), 404

# SUPERVISOR FUNCTIONS

# Display top 4 salesperson under supervisor (judging by win/lose)
@app.route("/supervisorTopSalesperson/<int:supervisor_id>")
def get_supervisor_top_salesperson(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT top 4 first_name, last_name, staff_email, SUM(CASE status WHEN 'win' THEN 1 ELSE 0 END) as win,
                    SUM(CASE status WHEN 'loss' THEN 1 ELSE 0 END) as loss
                    FROM dbo.quotation as QT
                    JOIN dbo.staff as ST ON QT.assigned_staff=ST.id 
                    WHERE ST.supervisor = ?
                    GROUP BY first_name, last_name, staff_email
                    ORDER BY win desc;''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display all the salesperson + their quotation analytics
@app.route("/salesperson/<int:supervisor_id>")
def get_salespersons_under_supervisor(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT first_name, last_name, staff_email, SUM(CASE status WHEN 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE status WHEN 'sent' THEN 1 ELSE 0 END) as sent,
    SUM(CASE status WHEN 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE status WHEN 'rejected' THEN 1 ELSE 0 END) as rejected
    FROM dbo.quotation as QT
    JOIN dbo.staff as ST ON QT.assigned_staff=ST.id 
    WHERE ST.supervisor = ?
    GROUP BY first_name, last_name, staff_email;''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display total quotation numbers of all salesperson under supervisor
@app.route("/supervisorQuotationNumbers/<int:supervisor_id>")
def get_quotations_numbers_supervisor(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT QT.status, COUNT(QT.Status) as num
    FROM dbo.staff as ST JOIN dbo.quotation as QT ON ST.id = QT.assigned_staff
    WHERE ST.supervisor = ?
    GROUP BY QT.status;''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display quotations from salespersons that needs approval
@app.route("/supervisorQuotationAttention/<int:supervisor_id>")
def get_supervisor_salesperson_pending_quotations(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT QT.quotation_no, C.company_name, QT.rfq_date, QT.assigned_staff, ST.first_name, ST.last_name
                    FROM quotation as QT, staff as ST, customer as C
                    WHERE ST.id = QT.assigned_staff and C.company_email = QT.customer_email and status = 'sent' and ST.supervisor=?''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Displays all quotations from salesperson under supervisor
@app.route("/supervisorAllQuotations/<int:supervisor_id>")
def get_supervisor_salesperson_quotations(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT QT.quotation_no, C.company_name, ST.first_name, ST.last_name, QT.assigned_staff, QT.rfq_date, status
                   FROM staff as ST, quotation as QT, customer as C
                   WHERE ST.id = QT.assigned_staff AND C.company_email = QT.customer_email AND ST.supervisor = ?''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Supervisor decision on quotation
@app.route("/supervisorQuotationDecision", methods=['POST'])
def supervisor_quotation_decision():
    data = request.get_json()
    print(data)
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE quotation
                SET status = ?, comment = ?
                WHERE quotation_no = ?
                ''', data["status"], data["comment"], data["quotation_no"])
    try:
        conn.commit()
        cursor.close()
        return jsonify(data), 201
    except Exception:
        cursor.close()
        return jsonify({
            "code": 404,
            "message": "Unable to commit to database."
        }), 404

# GENERAL FUNCTIONS

# Display all quotations
@app.route("/quotations")
def get_quotations():
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT CT.company_name as company, ST.first_name, ST.last_name, SUM(QCT.unit_price*QCT.quantity) as total_cost, SUM(QCT.quantity) as total_parts, QT.quotation_no, status FROM dbo.quotation as QT 
    INNER JOIN dbo.customer as CT ON QT.customer_email = CT.company_email
    INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
    INNER JOIN dbo.quotation_component as QCT ON QT.quotation_no = QCT.quotation_no
    GROUP BY QT.quotation_no, CT.company_name, ST.first_name, ST.last_name, status''')

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display all components under a specific quotation
@app.route("/quotationParts/<string:quotation_no>")
def get_quotation_parts(quotation_no):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT component_no, uom, description, quantity, CONVERT(varchar, unit_price*quantity) as total_price, is_bom, bom_no, remark, crawl_info, CONVERT(varchar, lvl) as level
    FROM dbo.quotation_component as QCT
    WHERE QCT.quotation_no = ?;''', quotation_no)

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

    cursor.close()
    return results

# Displays information for a specific quotation
@app.route("/quotationInfo/<string:quotation_no>")
def get_quotation_info(quotation_no):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT comment, status, first_name, last_name, company_name, supervisor, staff_email
    FROM dbo.quotation as QT
    INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
    INNER JOIN dbo.customer as CT ON QT.customer_email = CT.company_email
    WHERE QT.quotation_no = ?;''', quotation_no)

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

    cursor.close()
    return results

# Gets information about a specific component for editing purposes
@app.route("/partinfo/<string:component_no>")
def get_partinfo(component_no):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT crawl_info from dbo.quotation_component WHERE component_no = ?''', component_no)

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Get supervisor name
@app.route("/supervisorInfo/<int:supervisor_id>")
def get_supervisor_info(supervisor_id):
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''SELECT *
                    FROM staff
                    WHERE id = ?;''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

#for login required
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Staff.query.get(int(user_id))

#rbac
#ensure the login functionality is working: loginform not working
class Staff(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    staff_email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    supervisor = db.Column(db.String(255), nullable=False)

class LoginForm(FlaskForm):
    #enter email
    keyed_email = StringField(validators = [InputRequired(), Length(min = 4, max = 100 )], render_kw={"placeholder": "Email"})
    #enter password
    keyed_password = PasswordField(validators=[InputRequired(), Length(min = 4, max = 50)], render_kw={"placeholder": "Password"})
    #submit button with the word "Login"
    submit = SubmitField("Login")


@app.route("/login", methods = ['GET'])
def login():
    #get keyed email and password as objects and not strings
    
    #ISSUE: Email decoding issue when parsing into route 
    # you gotta use unquote(email) for the @ to appear but @ breaks your login code because its using the route, meaning it will instantly run unquote
    keyed_email = request.args.get('email')
    keyed_password = request.args.get('password')
    
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')

    cursor = conn.cursor()
    keyed_user = Staff.query.filter_by(staff_email = keyed_email).first()
    if keyed_user:
              #get hashed password
        hashed_pw = hashlib.sha256(keyed_password.encode('utf-8')).hexdigest()
        print(hashed_pw)
        #check if passwords match
        if hashed_pw == keyed_user.password:
            login_user(keyed_user)
            data = current_user.role
            #idk how this redirect(url_for) works so you gotta figure it out
            if data == "manager":
                return redirect('supervisor_home')
            elif data == "salesperson":
                return redirect(url_for('salesperson_home'))
            else:
                #should return something else to prevent error. MUST hve else statement
                return redirect(url_for('salesperson_home'))
    cursor.close()
    return render_template('login.html')

#2/2/2022: TO DO: map out
# 1. which link to redirect to once you login
# 2. which api route is open to which roles
# 3. ensure logout function is working -> which link to redirect to after logout?


    # form = LoginForm()
    # if form.validate_on_submit():
    #      keyed_user = Staff.query.filter_by(staff_email = form.keyed_email.data).first()
    #      if keyed_user:
    #           #get hashed password
    #         hashed_pw = hashlib.sha256(form.keyed_password.encode().hexdigest())
    #         print(hashed_pw)
    #         #  #check if passwords match
    #         if hashed_pw == keyed_user.password:
    #              login_user(keyed_user)
    #              return redirect(url_for('test'))
    # return render_template('login.html', form = LoginForm())


# @app.route('/login', methods = ['POST', 'GET'] )
# def login():
#     form = LoginForm()
#     return render_template('login.html', form = form) 


    # if request.method == 'POST':
    #     keyed_username = request.form['keyed_email']
    #     keyed_password = request.form['keyed_password']
    #     user=Staff.query.filter_by(keyed_email=form.staff_email.data).first()
    #     # username_result = cursor.execute("SELECT * FROM dbo.staff WHERE staff_email = %s", [keyed_username])

    #     #will need to check password validation again through SQL query instead -> checking if hashlib function working
    #     # user = cursor.execute("SELECT first_name FROM dbo.staff WHERE staff_email = %s", [keyed_username]).first()
    #     # role = cursor.execute("SELECT role from dbo.staff WHERE first_name =  %s", keyed_password) 
    #     if user:
    #         hashed_password = hashlib.sha256(keyed_password.encode())
    #         if keyed_password == hashed_password:
    #             login_user(user)
    #             #TO DO: need to ensure that logging in returns the user role
    #             return redirect(url_for('test'), )

    # else:
    #     #use a redirecting URL // module import
    #     return render_template("test.html")

#get the current user role logged in and display: FIXED
#able to get the role according to the login inputs :) YAY!!!
@app.route('/test', methods = ['GET', 'POST'])
@login_required
def test():
    print(current_user.role)
    return render_template("test.html", data = current_user.role)

#ISSUE: supervisor home not loading, current user.role has error when loaded.
@app.route('/supervisor_home')
@login_required
def supervisor_home():
    return render_template("supervisor_home.html", data = current_user.role)

#logout, clear session
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    #do you want to return index html??
    return render_template("index.html")

#template for inserting data
@app.route("/insert", methods=['POST'])
def insert():
    data = request.get_json()
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server='+forSQLServerName+';'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO dbo.quotation (quotation_id, customer_email, assigned_staff_email, rfq_date, status)
                VALUES
                (?, ?, ?, ?, ?)
                ''', data["quotation_id"], data["customer_email"], data["assigned_staff_email"], data["rfq_date"], data["status"])
    try:
        conn.commit()
        cursor.close()
        return jsonify(data), 201
    except Exception:
        cursor.close()
        return jsonify({
            "code": 404,
            "message": "Unable to commit to database."
        }), 404

@app.route("/")
def home():
    return "test"

# to be at the bottom
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)