from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import session
import hashlib
import urllib
import pyodbc

app = Flask(__name__)
params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=DESKTOP-KNDFRSA;DATABASE=myerp101;Trusted_Connection=yes;')
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
#i think the below line can remove
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://DESKTOP-7REM3J1\SQLEXPRESS/myerp101?driver=SQL+Server?trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

#put ur server name here
#desmond: DESKTOP-7REM3J1\SQLEXPRESS
#calvin: DESKTOP-1QKIK6R\SQLEXPRESS
#jingwen: DESKTOP-KNDFRSA
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-1QKIK6R\SQLEXPRESS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

@app.route("/quotations")
def get_quotations():
    cursor.execute('''SELECT CT.company_name as company, ST.first_name as contact, SUM(CQIT.unit_price*CQIT.qty) as total_cost, SUM(CQIT.qty) as total_parts, QT.quotation_no, status FROM dbo.quotation as QT 
    INNER JOIN dbo.customer as CT ON QT.customer_email = CT.company_email
    INNER JOIN dbo.staff as ST ON QT.assigned_staff = ST.id
    INNER JOIN dbo.crawled_quotation_item as CQIT ON QT.quotation_no = CQIT.quotation_no
    GROUP BY QT.quotation_no, CT.company_name, ST.first_name, status''')

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

    return results

@app.route("/salesperson/<int:supervisor_id>")
def get_salespersons_under_supervisor(supervisor_id):
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

    return results

@app.route("/supervisor_quotations_numbers/<int:supervisor_id>")
def get_quotations_numbers_supervisor(supervisor_id):
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

    return results

# TO DOOOO
# @app.route("/supervisor_quotations_attention/<int:supervisor_id>")
# def get_supervisor_salesperson_quotations(supervisor_id):
#     cursor.execute('''SELECT QT.status, COUNT(QT.Status) as num
#     FROM dbo.staff as ST JOIN dbo.quotation as QT ON ST.id = QT.assigned_staff
#     WHERE ST.supervisor = ?
#     GROUP BY QT.status;''', supervisor_id)
    
#     columns = [column[0] for column in cursor.description]
#     results = {}
#     i = 0
#     for row in cursor:
#         results[i] = dict(zip(columns, row))
#         i += 1

#     return results

# Displays all quotations from salesperson under supervisor
@app.route("/supervisor_all_quotations/<int:supervisor_id>")
def get_supervisor_salesperson_quotations(supervisor_id):
    cursor.execute('''SELECT QT.quotation_no, C.company_name, ST.first_name, ST.last_name, QT.rfq_date, status
                   FROM staff as ST, quotation as QT, customer as C
                   WHERE ST.id = QT.assigned_staff AND C.company_email = QT.customer_email AND ST.supervisor = ?''', supervisor_id)
    
    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

    return results

@app.route("/quotationParts/<string:quotation_no>")
def get_quotation_parts(quotation_no):
    print(quotation_no)
    cursor.execute('''SELECT component_no, uom, description, quantity, CONVERT(varchar, total_price) as total_price, is_drawing, drawing_no, set_no,
    STUFF((SELECT ','+CQIT.url, CQIT.supplier_name, CONVERT(varchar, CQIT.unit_price) as unit_price, CONVERT(varchar, CQIT.qty) as qty
    FROM dbo.crawled_quotation_item as CQIT WHERE QCT.quotation_no = CQIT.quotation_no AND QCT.row = CQIT.row for xml path('')),1,1,'') Concats
    FROM dbo.quotation_component as QCT
    WHERE QCT.quotation_no = ?;''', quotation_no)

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    print(results)
    return results
    
#rbac
#ensure the login functionality is working: TO DO
# @app.route("/login_data", methods = ['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         keyed_username = request.form['keyed_email']
#         keyed_password = request.form['keyed_password']

#         # username_result = cursor.execute("SELECT * FROM dbo.staff WHERE staff_email = %s", [keyed_username])

#         #will need to check password validation again through SQL query instead -> checking if hashlib function working
#         user = cursor.execute("SELECT * FROM dbo.staff WHERE staff_email = %s", [keyed_username]).first()
#         if user:
#             hashed_password = hashlib.sha256(keyed_password.encode())
#             if keyed_password == hashed_password:
#                 login_user(user)
#                 #TO DO: need to ensure that logging in returns the user role
#                 return render_template("test.html")
#     else:
#         #use a redirecting URL // module import
#         return render_template("test.html")

#get the current user role logged in and display: TO DO
#issue now is to make sure the roles are all displayed on the page properly
# @login_required
# def role_homepage():
#     print(current_user.role)
#     return render_template("index.html", data = current_user.role)

#logout, clear session
# @app.route('/logout', method = ['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     session.clear()
#     #do you want to return index html??
#     return render_template("index.html")

#template for inserting data
@app.route("/insert", methods=['POST'])
def insert():
    data = request.get_json()
    cursor.execute('''
                INSERT INTO dbo.quotation (quotation_id, customer_email, assigned_staff_email, rfq_date, status)
                VALUES
                (?, ?, ?, ?, ?)
                ''', data["quotation_id"], data["customer_email"], data["assigned_staff_email"], data["rfq_date"], data["status"])
    try:
        conn.commit()
        return jsonify(data), 201
    except Exception:
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