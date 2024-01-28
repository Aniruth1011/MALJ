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


## Accident Detection

We extract GyroScope and accelerometer values using In Built Sensors in android phones while user is driving. This is done in real time , and are stored as Json Files . We have our custom API's and these values are tracked .In case we detect any occurence of an accident , we immeditely notify it to the concerned authorities. We also give  other individuals in the same road travel advisories  regarding the accident in their preferred language . For this,we use Google API for machine translation to display it to them in their prefered language . So , we can cater to the linguistic need of a diverse population with multiple language requirements.



## Public Transport Prediction 

As of now , google maps approximately tells us when a given public transport is spposed to come , based on a previous plan . But , google map is unable to track any change in times , like any delayed or early arrival . So , We use  Tom Tom API , to track public vehicles , and thus estimate any early arrival or delayed arrival. So , now people can easily be notified or early or delayed arrivals , thus enabling smooth mobility .


##  Gamification 

In our attempt to spread public awareness ,we strive to make the public prefer public transport or walk to nearby areas . 
Thus we introduce a reward based system , where people who use public transport or walk short distances , are provided with in house reward points .

This Gamification aspect helps to spread awareness of environmental aspects of using Public Transport.

