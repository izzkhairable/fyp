from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://DESKTOP-7REM3J1\SQLEXPRESS/myerp101?driver=SQL+Server?trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

import pyodbc 

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-7REM3J1\SQLEXPRESS;'
                      'Database=myerp101;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()
cursor.execute('SELECT * FROM dbo.quotation')

for row in cursor:
    print(row)

conn.close()

class Quotations(db.Model):
    __tablename__ = 'dbo.quotation'

    quotation_id = db.Column(db.String, primary_key=True)
    customer_email = db.Column(db.String(64), nullable=False)
    assigned_staff_email = db.Column(db.String(64), nullable=False)
    rfq_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        '''
        converts the object into a dictionary.
        the keys respond to database columns
        '''
        columns = self.__mapper__.column_attrs.keys()
        result = {}
        for column in columns:
            result[column] = getattr(self, column)
        return result

@app.route("/quotations")
def get_quotations():
    quotationlist = Quotations.query.all()
    print(quotationlist)
    if len(quotationlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "quotations": [quotation.to_dict() for quotation in quotationlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no quotations available currently."
        }
    )

@app.route("/")
def home():
    return "test"


# to be at the bottom
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)