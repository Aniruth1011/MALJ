# Documentation for MALJ Flask Application

## Overview
This documentation provides an overview and explanation of the functionalities and endpoints of the MALJ Flask application. MALJ is designed to handle user registration, login, user details management, and sensor data handling for potential crash detection.

### Dependencies
- Flask: Web framework for building the application.
- Flask-CORS: Extension for handling Cross-Origin Resource Sharing.
- pymongo: Python driver for MongoDB.
- requests: Library for making HTTP requests.

### Configuration
- MongoDB: The application assumes a MongoDB instance running locally on the default port (27017).

## Endpoints

### 1. User Registration

- **Endpoint:** `/api/signup`
- **Method:** `POST`
- **Parameters:**
  - `phone_number`: Unique phone number for the user.
  - `password`: Password for the user account.
  - `details`: Additional details about the user.

#### Description
Registers a new user with the provided details. It checks if the user already exists before registration.

### 2. User Login

- **Endpoint:** `/api/login`
- **Method:** `POST`
- **Parameters:**
  - `phone_number`: User's phone number.
  - `password`: User's password.

#### Description
Authenticates a user based on the provided phone number and password.

### 3. Get User Details

- **Endpoint:** `/api/user_details/<phone_number>`
- **Method:** `GET`

#### Description
Retrieves details of a specific user identified by their phone number.

### 4. Update User Details

- **Endpoint:** `/api/user_details/<phone_number>`
- **Method:** `PUT`
- **Parameters:**
  - `details`: New details to update for the user.

#### Description
Updates details of a specific user identified by their phone number.

### 5. Store Stream Data

- **Endpoint:** `/api/stream_data/<phone_number>`
- **Method:** `POST`
- **Parameters:**
  - Sensor data: `gyroscope_value`, `accelerometer_value`, `location`.

#### Description
Stores sensor data for a user identified by their phone number. It also sends the data to another computer's API for potential crash detection.

### 6. Store Crash Data

- **Endpoint:** `/api/crash_data/<phone_number>`
- **Method:** `POST`
- **Parameters:**
  - `timestamp`: Timestamp of the crash.
  - `location`: Location of the crash.

#### Description
Stores crash data for a user identified by their phone number. It also sends the data to the user's API for further processing.

## Configuration
- The application runs on host `10.5.229.25` and port `5000`.
- It interacts with MongoDB running locally on the default port.
- It communicates with other services via HTTP requests.

## Running the Application
To run the application, execute the script in a Python environment where dependencies are installed. Make sure MongoDB is running locally before starting the Flask application. Use the provided host and port to access the endpoints.

```bash
python your_script_name.py
```

Replace `your_script_name.py` with the name of your Python script containing the Flask application code.