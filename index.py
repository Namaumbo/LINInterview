

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
CORS(app) 
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

def get_facilities_db():
    cursor = mysql.connection.cursor()
    sql = 'SELECT * FROM facility'
    cursor.execute(sql,[])
    res = cursor.fetchall()
    cursor.connection.commit()
    cursor.close()
    return res

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
    cursor.execute(sql, ( data['facility_name'],data['facility_code'],
                   data['district_id'], data['owner_id']),)
    cursor.connection.commit()
    cursor.close()
    return True

#     AND title LIKE '{title}%' LIMIT {limit} OFFSET {offset}"

def search_facilities(facility_name):
    cursor = mysql.connection.cursor()
    sql = f"SELECT * FROM facility WHERE facility_name = {facility_name} "
    cursor.execute(sql)
    data = cursor.fetchall()
    return data

def check_facility_name(facility_name):
    cursor = mysql.connection.cursor()
    facilities = get_facilities_db()
    sql = 'INSERT INTO `achived` (`facility_name` ) VALUES (%s)'
    for i in facilities['facilities']:
        if i['facility_name'] == facility_name:
            cursor.execute(sql,facility_name)
        




@app.route('/facilities', methods=['GET'])
def get_facilities():
    response = {}
    code = 200
    try:
        data = get_facilities_db()
        if (len(data) > 0):
            response['facilities'] = data
            response['message'] = 'success'
            code : 200


    except Exception as e:
        response['message'] = f"{e.args[0]}"
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
          
        # checking the distict id
            for district in districts:
                if district['id'] == facility_data['district_id']:
                    facility_data['district_id'] = district['id'] 
                    print(facility_data['district_id'])        
            for owner in owners:
                    if owner['id'] == facility_data['owner_id']:  
                        facility_data['owner_id'] = owner['id']      
                    
            sql_q = 'INSERT INTO `facility` (`facility_name`,`facility_code` , `district_id`,`owner_id` ) VALUES (%s,%s,%s,%s)'
            results = add_facility(sql_q , facility_data)

        if results:
            res['message'] = "item added successfully"
            code = 200
            res['status'] = 'success'
    
    except Exception as e:
        res['message'] = f"{e.args}"
        res['status'] = 'fail'
        res['description'] = 'Opps an error occurred'
        code = 500

    return jsonify(res),code


@app.route('/search-facility', methods=['GET'])
def search_facility():
    res = {}

    facility_data = {
        "facility_name":''
    }
    code =  200

    try:
        if (request.json.get('facility_name')):
            facility_data['facility_name'] = request.json.get('facility_name')
            data = search_facilities(facility_data['facility_name'])
            res['message'] = 'Facility found'
            res['facility'] = data
            code: 200

    except Exception as e:
        res['message'] = f"{e.args}"
        res['status'] = 'fail'
        res['description'] = 'Opps an error occurred'
        code = 500
    return(res),code

# @app.route('/achieve' methods=['GET'])
# def achieve():
#     res = {}

#     facility_name = {
#         'facility_name' :''
#     }
#     code = 200
#     try:
#         if (request.json.get('facility_name')):
#             facility_name['facility_name'] = request.json.get('facility_name')
#             results = check_facility_name(facility_name)


#     except Exception as e:
#         res['message'] = f"{e.args}"
#         res['status'] = 'fail'
#         res['description'] = 'Opps an error occurred'
#         code = 500
#     return(res),code

if __name__ == '__main__':
    app.run(host='0.0.0.0')
