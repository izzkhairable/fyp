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
import configparser
import math

import pyodbc

config = configparser.ConfigParser()
config.read('../sql_connect.cfg')

driver = config['database']['driver']
server = config['database']['server']
database = config['database']['database']
trusted_connection = config['database']['database']

app = Flask(__name__)
app.static_folder = 'static'
params = urllib.parse.quote_plus('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#i dont know how to configure secret key, but it is needed for flask_wtf
app.config['SECRET_KEY'] = 'thisisasecretkey'

db = SQLAlchemy(app)
CORS(app)

# SALESPERSON FUNCTIONS

# Updates database with edited information for each component
@app.route("/updateComponent", methods=['POST'])
def update_component():
    data = request.get_json()
    unit_price = round(data["unit_price"], 4)
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE dbo.quotation_component
                SET crawl_info = ?, unit_price = ?, quantity = ?
                WHERE id = ?
                ''', data["edited_crawl_info"], unit_price, data["qty"], data["id"])
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

# Updates database with edited information for each BOM
@app.route("/updateBomInfo", methods=['POST'])
def update_bom_info():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE dbo.quotation_component
                SET component_no = ?, uom = ?, description = ?, remark = ?
                WHERE id = ?
                ''', data["component_no"], data["uom"], data["description"], data["remark"], data["id"])
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

# Updates labour cost information for a specific quotation
@app.route("/updateLabourCost", methods=['POST'])
def update_labour_cost():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE dbo.quotation
                SET labour_cost = ?, labour_no_of_hours = ?, testing_cost = ?, markup_pct = ?, remark = ?
                WHERE quotation_no = ?
                ''', data["labour_cost"], data['labour_hours'], data['testing_cost'], data["markup"], data["labour_remarks"], data["quotation_no"])
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

# Updates quotation information
@app.route("/updateQuotationInfo", methods=['POST'])
def update_quotation_info():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE dbo.quotation
                SET comment = ?
                WHERE quotation_no = ?
                ''', data["comments"], data["quotation_no"])

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

# Delete component
@app.route("/deleteComponent", methods=['POST'])
def delete_component():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''
                DELETE FROM dbo.quotation_component
                WHERE quotation_no = ? AND id = ?
                ''', data["quotation_no"], data["id"])
    try:
        conn.commit()
        deleted_components = [int(data['id'])]
        row_level = cursor.execute("SELECT id, bom_id from dbo.quotation_component WHERE quotation_no = ? ORDER BY ROW ASC", data["quotation_no"])
        result = row_level.fetchall()
        for i in result:
            if i.bom_id in deleted_components:
                deleted_components.append(i.id)
                cursor.execute("DELETE FROM dbo.quotation_component WHERE quotation_no = ? AND id = ?", data["quotation_no"], i.id)
                conn.commit()
        row_level = cursor.execute("SELECT id, bom_id from dbo.quotation_component WHERE quotation_no = ? ORDER BY ROW ASC", data["quotation_no"])
        result = row_level.fetchall()
        row_no = 1
        for i in result:
            cursor.execute("UPDATE dbo.quotation_component SET row = ? WHERE quotation_no = ? AND id = ?", row_no, data["quotation_no"], i.id)
            conn.commit()
            row_no += 1

        cursor.close()
        return jsonify(data), 201
    except Exception:
        cursor.close()
        return jsonify({
            "code": 404,
            "message": "Unable to commit to database."
        }), 404

# Insert a new component under an existing BOM
@app.route("/insertComponentUnderBom", methods=['POST'])
def insert_component_under_bom():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    get_bom = cursor.execute("SELECT row, id, lvl FROM dbo.quotation_component WHERE quotation_no=? AND id=?", data["quotation_no"], data["id"])
    result = get_bom.fetchone()

    bom_id = result.id
    bom_lvl = math.ceil(result.lvl)
    bom_row = result.row
    insert_to = bom_row+1
    row_level = cursor.execute(
        "SELECT id from dbo.quotation_component where quotation_no=? and row >= ? ORDER BY ROW ASC", data['quotation_no'], insert_to)
    result = row_level.fetchall()
    row_no = insert_to+1
    for i in result:
        cursor.execute("UPDATE dbo.quotation_component SET row=? WHERE quotation_no=? AND id=?", row_no, data["quotation_no"], i.id)
        conn.commit()
        row_no+=1
    
    cursor.execute("INSERT INTO dbo.quotation_component(row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom, bom_id) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
    insert_to, data["quotation_no"], data["component_no"], bom_lvl+1, data["uom"], data["description"], 0, 0, int(data["is_bom"]), bom_id)

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

# Inserts a new component
@app.route("/insertComponent", methods=['POST'])
def insert_component():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    result = cursor.execute("SELECT COUNT(*) from dbo.quotation_component")
    rows = result.fetchone()
    row = rows[0] + 1
    cursor.execute('''
                INSERT INTO dbo.quotation_component(row, quotation_no, component_no, lvl, uom, description, quantity, unit_price, is_bom) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', row, data["quotation_no"], data["component_no"], 0.1, data["uom"], data["description"], 0, 0, data["is_bom"])
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT top 4 id, first_name, last_name, staff_email, SUM(CASE status WHEN 'win' THEN 1 ELSE 0 END) as win_no,
                    SUM(CASE status WHEN 'loss' THEN 1 ELSE 0 END) as loss_no,
                    SUM(CASE status WHEN 'win' THEN labour_cost ELSE 0 END) as earned,
                    SUM(CASE status WHEN 'loss' THEN labour_cost ELSE 0 END) as lost
                    FROM dbo.quotation as QT
                    JOIN dbo.staff as ST ON QT.assigned_staff=ST.id 
                    WHERE ST.supervisor = ?
                    GROUP BY id, first_name, last_name, staff_email
                    ORDER BY win_no desc;''', supervisor_id)
    
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT id, first_name, last_name, staff_email, SUM(CASE status WHEN 'approved' THEN 1 ELSE 0 END) as approved,
    SUM(CASE status WHEN 'sent' THEN 1 ELSE 0 END) as sent,
    SUM(CASE status WHEN 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE status WHEN 'rejected' THEN 1 ELSE 0 END) as rejected
    FROM dbo.quotation as QT
    JOIN dbo.staff as ST ON QT.assigned_staff=ST.id 
    WHERE ST.supervisor = ?
    GROUP BY id, first_name, last_name, staff_email;''', supervisor_id)
    
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT QT.quotation_no, C.company_name, QT.rfq_date, QT.assigned_staff, ST.first_name, ST.last_name
                    FROM quotation as QT, staff as ST, customer as C
                    WHERE ST.id = QT.assigned_staff and C.id = QT.customer and status = 'sent' and ST.supervisor=?''', supervisor_id)
    
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT QT.quotation_no, C.company_name, ST.first_name, ST.last_name, QT.assigned_staff, QT.rfq_date, status
                   FROM staff as ST, quotation as QT, customer as C
                   WHERE ST.id = QT.assigned_staff AND C.id = QT.customer AND ST.supervisor = ?
                   ORDER BY QT.rfq_date desc''', supervisor_id)
    
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
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

# Check if its the right supervisor before decision on quotation
@app.route("/supervisorCheck/<int:supervisor_id>/<string:quotation_no>")
def check_supervisor(supervisor_id, quotation_no):
    print(supervisor_id)
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT * from quotation, staff 
                   where staff.id = quotation.assigned_staff
                   and supervisor = ?
                   and quotation.quotation_no = ?''', supervisor_id, quotation_no)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display Total Win Loss for supervisor
@app.route("/supervisorWinLossAmount/<int:supervisor_id>")
def get_supervisor_win_loss(supervisor_id):
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT SUM(labour_cost) as total, status FROM dbo.quotation as QT 
                        INNER JOIN dbo.customer as CT ON QT.customer = CT.id
                        INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
                        WHERE status = 'win' or status = 'loss' and supervisor = ?
                        GROUP BY status''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# Display dashboard data for supervisor
@app.route("/supervisorDashboard/<int:supervisor_id>")
def get_supervisor_dashboard_data(supervisor_id):
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT year(rfq_date) as rfq_year, month(rfq_date) as rfq_month, status, COUNT(DISTINCT(QT.quotation_no)) as no_of_quotations, sum(labour_cost) as revenue,
                        sum(CASE when DATEDIFF(day, rfq_date, generation_date) < 12 THEN 1 ELSE 0 END) as on_time
                        FROM dbo.quotation as QT 
                        INNER JOIN dbo.customer as CT ON QT.customer = CT.id
                        INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
                        WHERE status = 'win' or status = 'loss' and supervisor = ?
                        GROUP BY status, rfq_date
                        ORDER BY rfq_date desc''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    cursor.close()
    return results

# GENERAL FUNCTIONS

# Display all quotations
@app.route("/quotations")
def get_quotations():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT CT.company_name as company, ST.first_name, ST.last_name, SUM(QCT.unit_price*QCT.quantity) as total_cost, SUM(QCT.quantity) as total_parts, QT.quotation_no, status FROM dbo.quotation as QT 
    INNER JOIN dbo.customer as CT ON QT.customer = CT.id
    INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
    LEFT JOIN dbo.quotation_component as QCT ON QT.quotation_no = QCT.quotation_no
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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT id, lvl, component_no, uom, description, quantity, unit_price, CONVERT(varchar, unit_price*quantity) as total_price, is_bom, bom_id, remark, crawl_info, CONVERT(varchar, lvl) as level
    FROM dbo.quotation_component as QCT
    WHERE QCT.quotation_no = ?
    ORDER BY row ASC;''', quotation_no)

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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT comment, status, first_name, last_name, company_name, supervisor, staff_email, markup_pct, labour_cost, labour_no_of_hours, testing_cost, remark
    FROM dbo.quotation as QT
    INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
    INNER JOIN dbo.customer as CT ON QT.customer = CT.id
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
@app.route("/partinfo/<string:id>")
def get_partinfo(id):
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    cursor.execute('''SELECT crawl_info from dbo.quotation_component WHERE id = ?''', id)

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
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
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

    def getFirstName(self):
        return self.first_name

@app.route("/login", methods = ['GET'])
def login():
    #get email and password as python objects, cannot parse into login as string
    keyed_email = request.args.get('email')
    keyed_password = request.args.get('password')
    
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
    cursor = conn.cursor()
    keyed_user = Staff.query.filter_by(staff_email = keyed_email).first()
    if keyed_user:
        #get hashed password
        hashed_pw = hashlib.sha256(keyed_password.encode('utf-8')).hexdigest()
        print(hashed_pw)
        #check if passwords match
        if hashed_pw == keyed_user.password:
            #set up variables
            login_user(keyed_user)
            role = current_user.role
            username = Staff.query.filter_by(staff_email = keyed_email).first().first_name
            #establish session with the logged in username and role
            session['username'] = username
            session['role'] = role
            session['logged_in'] =  True
            #check roles
            if role == "supervisor":
                return redirect(url_for('supervisor_home'))
            elif role == "salesperson":
                return redirect(url_for('salesperson_home'))
            else:
                #should return something else to prevent error. MUST hve else statement
                #only should have 3 roles, last will auto return admin page, must render template
                return render_template('admin.html')
    cursor.close()
    return render_template('login.html')

#routes need to ensure that their roles are correct.

#testing route // UNCOMMENT to test route and roles
# @app.route('/test', methods = ['GET', 'POST'])
# @login_required
# def test():
#     print(current_user.role)
#     return render_template("test.html", data = current_user.role)

#ROLES Guide:
#supervisor: can access both supervisor & salesperson pages
#salesperson only can access salesperson pages
#admin:

#login as supervisor, first page loaded
@app.route('/supervisor_home')
@login_required
def supervisor_home():
    if current_user.role == 'supervisor':
        #username = session['username']
        return render_template("supervisor_home.html")
    else:
        return render_template("unauthorised.html")

#login as salesperson, first page loaded
@app.route('/salesperson_home')
@login_required
def salesperson_home():
    if current_user.role == 'supervisor' or 'salesperson':
        return render_template("salesperson_home.html")
    else:
        return render_template("unauthorised.html")

#routing to supervisor_dashboard page
@app.route('/supervisor_dashboard')
@login_required
def supervisor_dashboard():
    if current_user.role == 'supervisor':
        return render_template("supervisor_dashboard.html")
    else:
        #return 404 error, not authorised to enter the page
        return render_template("unauthorised.html")

#routing to supervisor_quotation_decision
@app.route('/supervisor_quotation_decision')
@login_required
def supervisor_quotation_decision_page():
    if current_user.role == 'supervisor':
        return render_template("supervisor_quotation_decision.html")
    else:
        return render_template("unauthorised.html")
    
#routing to supervisor_quotation_template
@app.route('/supervisor_quotation_template')
@login_required
def supervisor_quotation_template_page():
    if current_user.role == 'supervisor':
        return render_template("supervisor_quotation_template.html")
    else:
        return render_template("unauthorised.html")
    
#routing to supervisor_view_quotes
@app.route('/supervisor_view_quotes')
@login_required
def supervisor_quotation_view_quotes_page():
    if current_user.role == 'supervisor':
        return render_template("supervisor_view_quotes.html")
    else:
        return render_template("unauthorised.html")

#routing to edit page
@app.route('/edit')
@login_required
def edit_page():
    #double check: can supervisor have access to edit pages?
    if current_user.role == 'supervisor' or 'salesperson':
        return render_template('edit.html')
    else:
        return render_template("unauthorised.html")

#routing to admin page
@app.route('/admin')
@login_required
def login_page():
    if current_user.role == 'admin':
        return render_template('admin.html')
    else:
        return render_template('unauthorised.html')

#logout, clear session
@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    #redirect back to login first, to be changed later
    return render_template("login.html")

#route wrapper header test
@app.route('/wrapper-test')
def route_test():
    return render_template("wrapper-test.html")

#template for inserting data
@app.route("/insert", methods=['POST'])
def insert():
    data = request.get_json()
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';Trusted_Connection='+trusted_connection+';')
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
    #for now will be returning the login page first
    return redirect(url_for('login'))


# to be at the bottom
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
    