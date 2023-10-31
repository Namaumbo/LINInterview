

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dotenv import load_dotenv
import requests
import uuid
from flask_mysqldb import MySQL


load_dotenv()
app = Flask(__name__)
facilities_api = os.getenv('facilities_api_main')
districts_api = os.getenv('districts_api_main')
owners_api = os.getenv('owners_api_main')
debug_mode = os.getenv('DEBUG')


app.debug = debug_mode
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'qwerty12'
app.config['MYSQL_DB'] = 'LINDB'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


def get_districts():

    districts = []
    res = requests.get(districts_api)
    districts = res.json()
    return districts


def get_owners():
    owners = []
    res = requests.get(owners_api)
    owners = res.json()
    return owners

def add_facility(sql , data):
    cursor = mysql.connection.cursor()
    cursor.execute(sql, (data['facility_code'], data['facility_name'],
                   data['district_id'], data['owner_id']),)
    cursor.connection.commit()
    cursor.close()
    return True



@app.route('/facilities', methods=['GET'])
def get_facilities():
    response = {}
    code = 200
    try:
        data = requests.get(facilities_api)
        response['data'] = data.json()

    except Exception as e:
        response['message'] = f"{e.__traceback__.tb_lineno}"
        response['status'] = 'fail'
        response['description'] = 'Opps an error occurred'
        code = 500
    return jsonify(response), code


# creating a facility
@app.route('/make-facility', methods=['POST'])
def create_facility():

    res = {}

    facility_data ={
        'facility_name': '',
        'facility_code': '',
        'district_id' : None,
        'owner_id' : None,
    }

    try:
        districts  = get_districts() #get all districts
        owners = get_owners() #get all owners


        if request.json.get('facility_name') and request.json.get('facility_code') and request.json.get('district_id') and request.json.get('owner_id'):
            facility_data['facility_name'] = request.json.get('facility_name')
            facility_data['facility_code']= str(uuid.uuid4())[:8].capitalize()
            facility_data['district_id'] = request.json.get('district_id')
            facility_data['owner_id'] = request.json.get('owner_id')

        # checking the distict id

            
            print(districts['id'])
            #  sql_q = 'INSERT INTO `todos` (`facility_name`,`facility_code` , `district_id`,`owner_id` ) VALUES (%s,%s,%s,%s)'
            #  results = add_facility(sql_q , facility_data)

        # if results:
        #     res['message'] = "item added successfully"
        #     code = 200
            res['status'] = 'success'
    
    except Exception as e:
        res['message'] = f"{e.args[0]}"
        res['status'] = 'fail'
        res['description'] = 'Opps an error occurred'
        code = 500

    return jsonify(res),code


if __name__ == '__main__':
    app.run(host='0.0.0.0')
