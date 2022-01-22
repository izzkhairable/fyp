from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import pyodbc 

app = Flask(__name__)
#i think the below line can remove
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://DESKTOP-7REM3J1\SQLEXPRESS/myerp101?driver=SQL+Server?trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-7REM3J1\SQLEXPRESS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

@app.route("/quotations")
def get_quotations():
    cursor.execute('''SELECT CT.company_name as company, ST.first_name as contact, SUM(CQIT.unit_price*CQIT.qty) as total_cost, SUM(CQIT.qty) as total_parts, QT.quotation_no, status FROM dbo.quotation as QT 
    INNER JOIN dbo.customer as CT ON QT.customer_email = CT.company_email
    INNER JOIN dbo.staff as ST ON QT.assigned_staff_email = ST.staff_email
    INNER JOIN dbo.crawled_quotation_item as CQIT ON QT.quotation_no = CQIT.quotation_no
    GROUP BY QT.quotation_no, CT.company_name, ST.first_name, status''')

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
    STUFF((SELECT ','+CQIT.url, CQIT.supplier_name, CONVERT(varchar, CQIT.unit_price) as unit_price, CONVERT(varchar, CQIT.qty) as qty from dbo.crawled_quotation_item as CQIT WHERE QCT.quotation_no = CQIT.quotation_no AND QCT.row = CQIT.row for xml path('')),1,1,'') Concats
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
    
#testing base for rbac
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        keyed_username = request.form['username']
        keyed_password = request.form['password']

        #get user
        username_result = cursor.execute("SELECT * FROM XXX WHERE username = %s", [keyed_username])

        if username_result != 0:
            password = cursor.fetchone()['password']

            #might need to implement password encryption
            #to check if logger info helps, if not change
            if password == keyed_password:
                app.logger.info("Login Successful")
            else:
                app.logger.info("Login Unsuccessful")
        else:
            app.logger.info("no user")
    # return render_template("login.html")
    else:
        #might need to set up a template folder
        #return render_template("login.html")

        #OR use a redirecting URL // module import
        return redirect(url_for("login.html"))



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