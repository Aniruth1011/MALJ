from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import requests
import pandas as pd
from sklearn.ensemble import IsolationForest
import json
from datetime import datetime
import torch
from transformers import RagRetriever, RagSequenceForGeneration, RagTokenizer
from geopy.distance import geodesic
import random
import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["MALJ"]
users_collection = db["users"]
stream_data_collection = db["stream_data"]
crash_data_collection = db["crash_data"]

# Variable to track whether a vehicle has been identified at a toll
identified_at_toll = set()

BUFFER_SIZE = 10

CRASH_MODEL_URL = 'http://10.5.229.17:5001/api/stream_data'

# USER_URL = 'http://10.5.228.40:5001/api/crash_data'

def get_distance(lat1, lon1, lat2, lon2):
    # Calculate distance between two geographic coordinates
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_traffic_conditions():
    return random.randint(0, 10)

# Function to predict actual arrival time based on planned time and traffic conditions
def predict_actual_arrival(planned_departure, planned_arrival, traffic_conditions):
    # Calculate the actual travel time based on planned time and traffic conditions
    planned_travel_time = planned_arrival - planned_departure
    actual_travel_time_seconds = max(0, planned_travel_time.total_seconds() - traffic_conditions)

    # Create a timedelta object with the calculated seconds
    actual_travel_timedelta = datetime.timedelta(seconds=actual_travel_time_seconds)

    # Calculate actual arrival time by adding timedelta to planned departure
    actual_arrival = planned_departure + actual_travel_timedelta

    return actual_arrival

def get_travel_advisory_with_rag(data, user_location):
   api_key = 'ZhmYKW91RCKGwN47qlsQMJFh4gWwfCHJ'
   coordinates = f"{data['location']['latitude']},{data['location']['longitude']}"
   endpoint = f'https://api.tomtom.com/search/2/reverseGeocode/{coordinates}.json'
   params = {
    'returnSpeedLimit': 'false',
    'radius': 10000,
    'returnRoadUse': 'false',
    'callback': 'cb',
    'allowFreeformNewLine': 'false',
    'returnMatchType': 'false',
    'view': 'Unified',
    'key': api_key
    }
   response = requests.get(endpoint, params=params)
   data = response.json()
   address = data.get('addresses')[0].get('address')

   model_name = 'facebook/rag-sequence-nq' # 'facebook/rag-token-nq'  # "facebook/dpr-ctx_encoder-single-nq-base"     #"facebook/rag-token-nq"  # Replace with your desired RAG model
   tokenizer = RagTokenizer.from_pretrained(model_name)
   retriever = RagRetriever.from_pretrained(model_name)
   #retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq", index_name="exact", use_dummy_dataset=True)

   #model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-nq", retriever=retriever)

   generator = RagSequenceForGeneration.from_pretrained(model_name)

   # Preprocess data
   latitude = data['location']['latitude']
   longitude = data['location']['longitude']
   location = address
   options = ['low', 'medium', 'high']
   congestion = random.choice(options)

   # Calculate distance from the accident location
   user_lat = user_location['latitude']
   user_lon = user_location['longitude']
   distance_km = get_distance(latitude, longitude, user_lat, user_lon)

   # Construct input text for retriever
   input_text = f"Accident at {location}. Distance: {distance_km:.2f} km. Latitude: {latitude}, Longitude: {longitude}. Gyroscope: {gyroscope}, Accelerometer: {accelerometer}. Congestion: {congestion}"

   # Retrieve relevant documents
   retriever_input = tokenizer(input_text, return_tensors='pt')
   retrieved_doc_ids, retrieved_doc_scores = retriever(retriever_input)

   # Construct prompt for generator
   prompt = "Assume that another person is traveling in a vehicle in the same path the above information is related to. Make an informative traffic advisory message highlighting why he should avoid this path, and how far from the accident he is. Be more informative, using insights from the retrieved documents."

   # Generate advisory message with retrieved documents
   generator_input = tokenizer(prompt, retrieved_doc_ids, return_tensors='pt')
   generated_ids = generator.generate(generator_input)
   travel_advisory_message = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

   return travel_advisory_message

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

        travel_advisory_message = get_travel_advisory_with_rag(crash_data, {"latitude": 1, "longitude": 1})

        # Insert crash data into the 'crash_data' collection
        crash_data_collection.insert_one(crash_data)

        return jsonify({'crash_data':crash_data, 'advise': travel_advisory_message})

    vehicle_numbers = user['details'].get('vehicle_number', [])

    for vehicle_number in vehicle_numbers:
        if vehicle_number in identified_at_toll:
            identified_at_toll.remove(vehicle_number)
            return jsonify({'message': f'Vehicle {vehicle_number} has been identified at a toll'})


    return jsonify({'message': 'Sensor data stored successfully'})

@app.route('/api/predict_arrival', methods=['POST'])
def predict_arrival():
    data = request.get_json()

    # Check if all required fields are present in the request
    required_fields = ['planned_departure', 'planned_arrival']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Parse input data
    planned_departure = datetime.datetime.strptime(data['planned_departure'], '%Y-%m-%d %H:%M:%S')
    planned_arrival = datetime.datetime.strptime(data['planned_arrival'], '%Y-%m-%d %H:%M:%S')
    traffic_conditions = get_traffic_conditions()

    # Call the prediction function
    actual_arrival = predict_actual_arrival(planned_departure, planned_arrival, traffic_conditions)

    # Return the result
    return jsonify({'actual_arrival': actual_arrival.strftime('%Y-%m-%d %H:%M:%S')})

@app.route('/api/toll_gate', methods=['POST'])
def toll_gate():
    # Assuming you receive the vehicle number in the request
    data = request.get_json()
    vehicle_number = data.get('vehicle_number')

    # Update the identified_at_toll set
    for i in vehicle_number:
        identified_at_toll.add(i)

    return jsonify({'Vehicles': vehicle_number})

if __name__ == '__main__':
    app.run(host='10.5.229.25', port=5000, debug=True)