
---

# MALJ System Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [API Endpoints](#api-endpoints)
    - [3.1 /api/signup](#api-signup)
    - [3.2 /api/login](#api-login)
    - [3.3 /api/user_details/<phone_number>](#api-user-details)
    - [3.4 /api/user_details/<phone_number> (PUT)](#api-update-user-details)
    - [3.5 /api/stream_data/<phone_number> (POST)](#api-stream-data)
    - [3.6 /api/predict_arrival (POST)](#api-predict-arrival)
    - [3.7 /api/toll_gate (POST)](#api-toll-gate)
4. [Functions](#functions)
    - [4.1 get_distance(lat1, lon1, lat2, lon2)](#function-get-distance)
    - [4.2 get_traffic_conditions()](#function-get-traffic-conditions)
    - [4.3 predict_actual_arrival(planned_departure, planned_arrival, traffic_conditions)](#function-predict-actual-arrival)
    - [4.4 get_travel_advisory_with_rag(data, user_location)](#function-get-travel-advisory)
    - [4.5 process_sensor_data(json_data)](#function-process-sensor-data)
    - [4.6 detect_accident_from_json(data, contamination)](#function-detect-accident)
5. [Running the Application](#running-the-application)

---

## 1. Introduction<a name="introduction"></a>

The MALJ System is a Flask-based application designed for user registration, login, real-time sensor data processing, crash detection, and travel advisory generation. This documentation provides an overview of its features and functionalities.

## 2. Dependencies<a name="dependencies"></a>

The system relies on the following Python libraries and services:

- Flask
- Flask-CORS
- pymongo
- requests
- pandas
- scikit-learn (IsolationForest)
- torch (PyTorch)
- transformers
- geopy

## 3. API Endpoints<a name="api-endpoints"></a>

### 3.1 /api/signup<a name="api-signup"></a>

**Method:** POST

**Input:**
- `phone_number`: User's phone number
- `password`: User's password
- `details`: Additional user details

**Output:**
- Success: `{'message': 'User registered successfully'}`
- Error: `{'error': 'User already exists'}`

### 3.2 /api/login<a name="api-login"></a>

**Method:** POST

**Input:**
- `phone_number`: User's phone number
- `password`: User's password

**Output:**
- Success: `{'message': 'Login successful'}`
- Error: `{'error': 'Invalid username or password'}`

### 3.3 /api/user_details/<phone_number><a name="api-user-details"></a>

**Method:** GET

**Output:**
- Success: User details as JSON
- Error: `{'error': 'User not found'}`

### 3.4 /api/user_details/<phone_number> (PUT)<a name="api-update-user-details"></a>

**Method:** PUT

**Input:**
- `details`: New user details

**Output:**
- Success: `{'message': 'User details updated successfully'}`
- Error: `{'error': 'User not found'}`

### 3.5 /api/stream_data/<phone_number> (POST)<a name="api-stream-data"></a>

**Method:** POST

**Input:**
- `gyroscope_value`: Gyroscope data
- `accelerometer_value`: Accelerometer data
- `location`: User's location

**Output:**
- Success: `{'message': 'Sensor data stored successfully'}` or crash data with advisory message
- Error: `{'error': 'User not found'}`

### 3.6 /api/predict_arrival (POST)<a name="api-predict-arrival"></a>

**Method:** POST

**Input:**
- `planned_departure`: Planned departure time (format: `%Y-%m-%d %H:%M:%S`)
- `planned_arrival`: Planned arrival time (format: `%Y-%m-%d %H:%M:%S`)

**Output:**
- Success: `{'actual_arrival': 'YYYY-MM-DD HH:MM:SS'}`

### 3.7 /api/toll_gate (POST)<a name="api-toll-gate"></a>

**Method:** POST

**Input:**
- `vehicle_number`: List of vehicle numbers identified at a toll

**Output:**
- Success: `{'Vehicles': vehicle_number}`

## 4. Functions<a name="functions"></a>

### 4.1 get_distance(lat1, lon1, lat2, lon2)<a name="function-get-distance"></a>

Calculates the distance between two geographic coordinates using the Haversine formula.

### 4.2 get_traffic_conditions()<a name="function-get-traffic-conditions"></a>

Generates the traffic conditions.

### 4.3 predict_actual_arrival(planned_departure, planned_arrival, traffic_conditions)<a name="function-predict-actual-arrival"></a>

Predicts the actual arrival time based on planned departure, planned arrival, and traffic conditions.

### 4.4 get_travel_advisory_with_rag(data, user_location)<a name="function-get-travel-advisory"></a>

Generates a travel advisory message using the RAG (Retrieval-Augmented Generation) model based on accident data and user location.

### 4.5 process_sensor_data(json_data)<a name="function-process-sensor-data"></a>

Processes raw sensor data from the client and returns a Pandas DataFrame.

### 4.6 detect_accident_from_json(data, contamination)<a name="function-detect-accident"></a>

Utilizes Isolation Forest to detect anomalies in the processed sensor data. If anomalies are detected, it assumes an accident.

## 5. Running the Application<a name="running-the-application"></a>

To run the application, execute the script with the following command:

```bash
python app.py
```

The application will run on the specified host and port.

---

This documentation provides an in-depth guide to the MALJ System, including its API endpoints and underlying functions. Users can reference this documentation for efficient utilization of the system.