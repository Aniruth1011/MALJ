from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import requests
import pandas as pd
from sklearn.ensemble import IsolationForest
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["MALJ"]
users_collection = db["users"]
stream_data_collection = db["stream_data"]
crash_data_collection = db["crash_data"]

BUFFER_SIZE = 10

CRASH_MODEL_URL = 'http://10.5.229.17:5001/api/stream_data'

# USER_URL = 'http://10.5.228.40:5001/api/crash_data'

def process_sensor_data(json_data):

    acc_x = json_data['accelerometer_value']['acc_x']
    acc_y = json_data['accelerometer_value']['acc_y']
    acc_z = json_data['accelerometer_value']['acc_z']

    gyro_x = json_data['gyroscope_value']['gyro_x']
    gyro_y = json_data['gyroscope_value']['gyro_y']
    gyro_z = json_data['gyroscope_value']['gyro_z']

    # Create a dictionary with sensor data
    sensor_data = {
        'x_accel': acc_x,
        'y_accel': acc_y,
        'z_accel': acc_z,
        'x_gyro': gyro_x,
        'y_gyro': gyro_y,
        'z_gyro': gyro_z,
    }

    # Create a DataFrame from the dictionary
    processed_data = pd.DataFrame([sensor_data])
    processed_data['acceleration_magnitude'] = (processed_data['x_accel']**2 + processed_data['y_accel']**2 + processed_data['z_accel']**2)**0.5
    processed_data['gyro_magnitude'] = (processed_data['x_gyro']**2 + processed_data['y_gyro']**2 + processed_data['z_gyro']**2)**0.5

    # Add 'location' data if needed
    processed_data['location'] = json_data.get('location', None)

    return processed_data

def detect_accident_from_json(data, contamination=0.0005):
    # Load JSON file
    json_data = data

    # Process sensor data
    processed_data = process_sensor_data(json_data)

    # Combine selected features
    features = ['acceleration_magnitude', 'gyro_magnitude']

    X = processed_data[features]

    # Fit Isolation Forest model
    model = IsolationForest(contamination=contamination)
    processed_data['anomaly_score'] = model.fit_predict(X)

    # Identify anomalies
    anomalies = processed_data[processed_data['anomaly_score'] == -1]

    # If anomalies are detected, consider it as an accident
    if not anomalies.empty:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        location = anomalies['location'].iloc[-1]
        print("Accident Detected at {} with location: {}".format(timestamp, location))
        return {
            'timestamp': timestamp,
            'location': location,
            'accident_detected': True
        }
    else:
        print("No Accident Detected.")
        return {
            'timestamp': None,
            'location': None,
            'accident_detected': False
        }

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    phone_number = data.get('phone_number')
    password = data.get('password')
    details = data.get('details')

    # Check if the username already exists
    if users_collection.find_one({'phone_number': phone_number}):
        return jsonify({'error': 'User already exists'}), 400

    # Insert the new user into the 'users' collection
    users_collection.insert_one({'phone_number': phone_number, 
                                 'password': password, 
                                 'details': details
                                 })

    return jsonify({'message': 'User registered successfully'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    phone_number = data.get('phone_number')
    password = data.get('password')

    # Check if the username and password match an existing user
    user = users_collection.find_one({'phone_number': phone_number, 
                                      'password': password
                                      })

    if user:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
    
@app.route('/api/user_details/<phone_number>', methods=['GET'])
def get_user_details(phone_number):
    # Retrieve user details from the 'users' collection based on phone number
    user = users_collection.find_one({'phone_number': phone_number})

    if user:
        user_details = {
            'phone_number': user['phone_number'],
            'details': user.get('details', '')
        }
        return jsonify(user_details)
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/api/user_details/<phone_number>', methods=['PUT'])
def update_user_details(phone_number):
    data = request.get_json()
    new_details = data.get('details')

    # Update user details in the 'users' collection based on phone number
    result = users_collection.update_one({'phone_number': phone_number}, {'$set': {'details': new_details}})

    if result.modified_count > 0:
        return jsonify({'message': 'User details updated successfully'})
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/api/stream_data/<phone_number>', methods=['POST'])
def store_stream_data(phone_number):
    data = request.get_json()
    gyroscope_value = data.get('gyroscope_value')
    accelerometer_value = data.get('accelerometer_value')
    location = data.get('location')

    # Check if the user exists in the 'users' collection
    user = users_collection.find_one({'phone_number': phone_number})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Retrieve existing stream data or create a new entry
    stream_data_entry = stream_data_collection.find_one({'phone_number': phone_number})

    if stream_data_entry:
        # Get the existing stream data list or create a new one
        stream_data_list = stream_data_entry.get('stream_data', [])
    else:
        stream_data_list = []

    # Append the new sensor data to the list
    stream_data_list.append({
        'gyroscope_value': gyroscope_value,
        'accelerometer_value': accelerometer_value,
        'location': location
    })

    # Trim the list to the last BUFFER_SIZE elements
    stream_data_list = stream_data_list[-BUFFER_SIZE:]

    # Update or insert the stream data entry in the 'stream_data' collection
    stream_data_collection.update_one({'phone_number': phone_number}, {'$set': {'stream_data': stream_data_list}}, upsert=True)

    # Detect anomalies using Isolation Forest
    anomalies = detect_accident_from_json(data)

    if anomalies['accident_detected']:
        # If anomalies are detected, assume a crash and store crash data
        crash_timestamp = anomalies['timestamp']
        location = {'latitude': location['latitude'], 'longitude': location['longitude']}

        crash_data = {
            'phone_number': phone_number,
            'timestamp': crash_timestamp,
            'location': location,
            'accident_detected': True
        }
        # Insert crash data into the 'crash_data' collection
        crash_data_collection.insert_one(crash_data)

        return jsonify(crash_data)

    return jsonify({'message': 'Sensor data stored successfully'})

if __name__ == '__main__':
    app.run(host='10.5.229.25', port=5000, debug=True)