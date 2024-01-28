
---

# Project Documentation: MALJ System

## Table of Contents
1. [Introduction](#introduction)
2. [Dependencies](#dependencies)
3. [API Endpoints](#api-endpoints)
   - [1. /api/signup](#1-api-signup)
   - [2. /api/login](#2-api-login)
   - [3. /api/user_details/<phone_number>](#3-api-user-detailsphone_number)
   - [4. /api/user_details/<phone_number> (PUT)](#4-api-user-detailsphone_number-put)
   - [5. /api/stream_data/<phone_number> (POST)](#5-api-stream-dataphone_number-post)
4. [Sensor Data Processing](#sensor-data-processing)
   - [1. process_sensor_data(json_data)](#1-process_sensor_datajson_data)
   - [2. detect_accident_from_json(data, contamination)](#2-detect_accident_from_jsondata-contamination)
5. [RAG Model Integration](#rag-model-integration)
   - [get_travel_advisory_with_rag(data, user_location)](#get_travel_advisory_with_ragdata-user_location)
6. [Server Configuration](#server-configuration)
   - [Run the Application](#run-the-application)

---

## 1. Introduction<a name="introduction"></a>

The MALJ System is a Flask-based web application designed to handle user sign-up, login, and real-time sensor data processing. The system detects anomalies in the sensor data and provides travel advisories using a Transformer-based model.

## 2. Dependencies<a name="dependencies"></a>

The MALJ System utilizes the following Python libraries and external services:

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

### 1. /api/signup<a name="1-api-signup"></a>

**Method:** POST

**Input:**
- `phone_number`: User's phone number
- `password`: User's password
- `details`: Additional user details

**Output:**
- Success: `{'message': 'User registered successfully'}`
- Error: `{'error': 'User already exists'}`

### 2. /api/login<a name="2-api-login"></a>

**Method:** POST

**Input:**
- `phone_number`: User's phone number
- `password`: User's password

**Output:**
- Success: `{'message': 'Login successful'}`
- Error: `{'error': 'Invalid username or password'}`

### 3. /api/user_details/<phone_number><a name="3-api-user-detailsphone_number"></a>

**Method:** GET

**Output:**
- Success: User details as JSON
- Error: `{'error': 'User not found'}`

### 4. /api/user_details/<phone_number> (PUT)<a name="4-api-user-detailsphone_number-put"></a>

**Method:** PUT

**Input:**
- `details`: New user details

**Output:**
- Success: `{'message': 'User details updated successfully'}`
- Error: `{'error': 'User not found'}`

### 5. /api/stream_data/<phone_number> (POST)<a name="5-api-stream-dataphone_number-post"></a>

**Method:** POST

**Input:**
- `gyroscope_value`: Gyroscope data
- `accelerometer_value`: Accelerometer data
- `location`: User's location

**Output:**
- Success: `{'message': 'Sensor data stored successfully'}` or crash data with advisory message
- Error: `{'error': 'User not found'}`

## 4. Sensor Data Processing<a name="sensor-data-processing"></a>

### 1. process_sensor_data(json_data)<a name="1-process_sensor_datajson_data"></a>

This function processes raw sensor data from the client, calculates magnitude values, and returns a Pandas DataFrame.

### 2. detect_accident_from_json(data, contamination)<a name="2-detect_accident_from_jsondata-contamination"></a>

This function utilizes Isolation Forest to detect anomalies in the processed sensor data. If anomalies are detected, it assumes an accident.

## 5. RAG Model Integration<a name="rag-model-integration"></a>

### get_travel_advisory_with_rag(data, user_location)<a name="get_travel_advisory_with_ragdata-user_location"></a>

This function generates a travel advisory message using the RAG (Retrieval-Augmented Generation) model based on accident data and user location.

## 6. Server Configuration<a name="server-configuration"></a>

To run the application, execute the script with the following command:

```bash
python app.py
```

The application will run on the specified host and port.

---

This documentation provides an overview of the MALJ System, its endpoints, data processing functions, and integration with the RAG model. Users can refer to this documentation for understanding and utilizing the system effectively.