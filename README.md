# MALJ

This is the README file for the project. 

## API Documentation

For API documentation, please refer to the [API Documentation](BackEnd/API_DOCUMENTATION.md) file located in the "BackEnd" folder.




## Automated Toll Management

While the use of Fastag has indeed reduced waiting time at toll gates a lot , incoming vehicles still have to wait at the toll booth to get the Fastag scanned . 
We thus implement the novel solution of scanning the Number Plate of vehicles in Real Time , thus removing the need to wait at Toll Booth's. 
Using the vehicle number plate , we can easily exact the toll from their accounts. 

    ## Libraries Used
    opencv-python 
    numpy 
    easyocr 
    os 
    tensorflow


## Technical Implementation 

We used pre trained weights for number plate detection. We are attaching the links for the weights we used [Number Plate Detection Weights](https://github.com/ksingh7/ml_experiments/tree/main/convert_keras_model_to_tensorflow/models) . 

Once any vehcile appears within the Camera Point of View Frame , this automatically detects the number plate . 
Once the number plate has been Detected , we use EasyOCR to get the exact number plate text. 

We have access to the number plates against the car owners , using which we can efficiently exact toll. 

The key importance of this feature is that vehicles no longer need to wait 
