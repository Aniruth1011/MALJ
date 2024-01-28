from google.colab.patches import cv2_imshow
import cv2
from os.path import splitext
from tensorflow.keras.models import model_from_json
import easyocr


cap = cv2.VideoCapture('/content/drive/MyDrive/Toll_Video.mp4')
fps = cap.get(cv2.CAP_PROP_FPS)
delay_ms = int(1000 / fps)

def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        print("Model Loaded successfully...")
        return model
    except Exception as e:
        print(e)

wpod_net_path = r'/content/wpod-net.h5'
model = load_model(wpod_net_path)

custom_config = r'--oem 3 --psm 6'

def read_frame(frame):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(frame)
    text = ""  # Initialize text before the loop

    for (bbox, result_text, prob) in results:
        print(f'Text: {result_text}, Probability: {prob}')
        text += result_text + " "  # Update the value of text

    return text.strip(), frame  # Return the updated text

def preprocess_image(image_path, resize=False):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224, 224))
    return img

if not cap.isOpened():
    print("Error opening video file")
    exit()

i = 0

while True:
    # Capture frame-by-frame
    if (i%10000==0):
        ret, frame = cap.read()

        # Check if the video has ended
        if not ret:
            break

        read_frame_mark, text_ = read_frame(frame)

        # Display the frame (you can replace this with your processing logic)
        cv2_imshow(frame)

        print(i , text_)
        # Break the loop if 'q' key is pressed
        if cv2.waitKey(delay_ms) & 0xFF == ord('q'):
            break
    i+=1

# Release the video capture object and close the window
cap.release()
cv2.destroyAllWindows()