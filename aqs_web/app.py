from flask import Flask, request, jsonify
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
    cursor.execute('''SELECT CT.company_name as company, ST.first_name as contact, SUM(SSIT.unit_price*SSIT.qty) as total_cost, SUM(SSIT.qty) as total_parts, QT.quotation_id, status FROM dbo.quotation as QT 
    INNER JOIN dbo.customer as CT ON QT.customer_email = CT.company_email
    INNER JOIN dbo.staff as ST ON QT.assigned_staff_email = ST.staff_email
    INNER JOIN dbo.supplier_source_item as SSIT ON QT.quotation_id = SSIT.quotation_id
    GROUP BY QT.quotation_id, CT.company_name, ST.first_name, status''')

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

    return results

@app.route("/quotationParts/<string:quotation_id>")
def get_quotation_parts(quotation_id):
    print(quotation_id)
    cursor.execute('''SELECT QIT.mfg_pn, QIT.uom, QIT.description, QIT.qty, CONVERT(varchar, SSIT.unit_price) as price, SSIT.unit_price*SSIT.qty as sub_total, ST.supplier_name, ST.supplier_website FROM dbo.quotation_item as QIT 
    INNER JOIN dbo.supplier_source_item as SSIT on QIT.quotation_id = SSIT.quotation_id AND QIT.mfg_pn = SSIT.mfg_pn
    INNER JOIN dbo.supplier as ST on SSIT.supplier_id = ST.supplier_id
    WHERE QIT.quotation_id = ?''', quotation_id)

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1
    print(results)
    return results

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