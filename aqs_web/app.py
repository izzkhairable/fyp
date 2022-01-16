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

#template for getting data
@app.route("/test")
def test():
    cursor.execute('SELECT * FROM dbo.quotation')

    columns = [column[0] for column in cursor.description]
    results = {}
    i = 0
    for row in cursor:
        results[i] = dict(zip(columns, row))
        i += 1

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