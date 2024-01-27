from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import requests

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["MALJ"]
users_collection = db["users"]
stream_data_collection = db["stream_data"]
crash_data_collection = db["crash_data"]

BUFFER_SIZE = 10

CRASH_MODEL_URL = 'http://10.5.229.17:5001/api/stream_data'

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

    # Send data to the other computer's API
    try:
        response = requests.post(CRASH_MODEL_URL, json=data)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print('Data sent to the other computer successfully')
    except requests.exceptions.RequestException as e:
        print(f'Error sending data to the other computer: {e}')

    return jsonify({'message': 'Sensor data stored and sent successfully'})

@app.route('/api/crash_data/<phone_number>', methods=['POST'])
def store_crash_data(phone_number):
    data = request.get_json()
    crash_timestamp = data.get('timestamp')

    # Insert crash data into the 'crash_data' collection
    crash_data_collection.insert_one({
        'phone_number': phone_number,
        'timestamp': crash_timestamp,
    })

    return jsonify({'message': 'Crash data stored successfully'})


if __name__ == '__main__':
    app.run(debug=True)