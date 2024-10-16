from flask import Flask, request, jsonify
from tensorflow.keras.applications import DenseNet121
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from flask_cors import CORS  
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import os
import firebase_admin
from firebase_admin import credentials, firestore, storage

app = Flask(__name__)
CORS(app)  

cred = credentials.Certificate('../frontend/airecondrone-firebase-adminsdk-1oiv0-cfdb4ae33a.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'airecondrone.appspot.com'  
})

db = firestore.client()
bucket = storage.bucket()

print("Loading model...")
try:
    base_model = DenseNet121(include_top=False, weights=None, input_shape=(64, 64, 3))
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    predictions = Dense(200, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    MODEL_PATH = 'optimal_densenet.keras'
    if os.path.exists(MODEL_PATH):
        model.load_weights(MODEL_PATH)
        print("Model weights loaded successfully.")
    else:
        raise FileNotFoundError(f"Model weights not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading the model: {e}")

CLASS_NAMES = ['墨.png', '竟.png', '章.png', '隐.png', '隔.png', '隘.png', '隙.png', '障.png', '隧.png',
               '隶.png', '难.png', '雀.png', '雁.png', '雄.png', '雅.png', '集.png', '雇.png', '雌.png',
               '雍.png', '雏.png', '雕.png', '雨.png', '雪.png', '零.png', '雷.png', '雹.png', '雾.png',
               '需.png', '霄.png', '震.png', '霉.png', '霍.png', '霓.png', '霖.png', '霜.png', '霞.png',
               '露.png', '霸.png', '霹.png', '青.png', '靖.png', '静.png', '靛.png', '非.png', '靠.png',
               '靡.png', '面.png', '革.png', '靳.png', '靴.png', '靶.png', '鞋.png', '鞍.png', '鞘.png',
               '鞠.png', '鞭.png', '韦.png', '韧.png', '韩.png', '韭.png', '音.png', '韵.png', '韶.png',
               '页.png', '顶.png', '顷.png', '项.png', '顺.png', '须.png', '顽.png', '顾.png', '顿.png',
               '颁.png', '颂.png', '预.png', '颅.png', '领.png', '颇.png', '颈.png', '颊.png', '颐.png',
               '频.png', '颓.png', '颖.png', '颗.png', '题.png', '颜.png', '额.png', '颠.png', '颤.png',
               '颧.png', '风.png', '飘.png', '飞.png', '食.png', '餐.png', '饥.png', '饭.png', '饮.png',
               '饯.png', '饰.png', '饱.png', '饲.png', '饵.png', '饶.png', '饺.png', '饼.png', '饿.png',
               '馁.png', '馅.png', '馆.png', '馈.png', '馋.png', '馏.png', '馒.png', '首.png', '香.png',
               '马.png', '驭.png', '驮.png', '驯.png', '驰.png', '驱.png', '驳.png', '驴.png', '驶.png',
               '驹.png', '驻.png', '驼.png', '驾.png', '骂.png', '骄.png', '骆.png', '骇.png', '骋.png',
               '验.png', '骏.png', '骑.png', '骗.png', '骚.png', '骡.png', '骤.png', '骨.png', '骸.png',
               '髓.png', '高.png', '鬃.png', '鬼.png', '魁.png', '魂.png', '魄.png', '魏.png', '魔.png',
               '鱼.png', '鲁.png', '鲍.png', '鲜.png', '鲤.png', '鲸.png', '鳃.png', '鳖.png', '鳞.png',
               '鸟.png', '鸡.png', '鸣.png', '鸥.png', '鸦.png', '鸭.png', '鸯.png', '鸳.png', '鸵.png',
               '鸽.png', '鸿.png', '鹃.png', '鹅.png', '鹊.png', '鹏.png', '鹤.png', '鹰.png', '鹿.png',
               '麓.png', '麦.png', '麻.png', '黄.png', '黍.png', '黎.png', '黑.png', '黔.png', '默.png',
               '鼎.png', '鼓.png', '鼠.png', '鼻.png', '齐.png', '齿.png', '龄.png', '龋.png', '龙.png',
               '龚.png', '龟.png']

@app.route('/')
def home():
    return "<h1>Welcome to the Image Classification API</h1><p>Use the /predict endpoint to upload an image for classification.</p>"

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        file_content = file.read()

        # Upload the image to Firebase Storage
        blob = bucket.blob(file.filename)
        blob.upload_from_file(io.BytesIO(file_content), content_type=file.content_type)

        # URL-encode the filename to handle spaces and special characters
        image_path = file.filename.replace(" ", "%20")  # Replace spaces with %20
         
        # Construct the Firebase Storage URL
        image_url = f"https://firebasestorage.googleapis.com/v0/b/airecondrone.appspot.com/o/{image_path}?alt=media"

        # Prepare the image for prediction
        img = Image.open(io.BytesIO(file_content))
        img = img.resize((64, 64))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array.astype('float32') / 255.0 

        # Make predictions
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]

        # Save the prediction to Firestore
        doc_ref = db.collection('predictions').add({
            'predicted_class': CLASS_NAMES[predicted_class],
            'file_name': file.filename,
            'image_url': image_url,  
            'timestamp': firestore.SERVER_TIMESTAMP
        })

        _, doc_ref = doc_ref
        document_id = doc_ref.id  

        return jsonify({'predicted_class': CLASS_NAMES[predicted_class], 'document_id': document_id, 'image_url': image_url})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recent-image', methods=['GET'])
def get_recent_image():
    try:
        # Retrieve the most recent document from Firestore
        predictions_ref = db.collection('predictions').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1)
        recent_prediction = predictions_ref.get()

        if recent_prediction:
            recent_doc = recent_prediction[0].to_dict()
            return jsonify({'image_url': recent_doc['image_url']}), 200
        else:
            return jsonify({'error': 'No predictions found'}), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


def get_exif_data(image):
    """Extract EXIF data from an image."""
    exif_data = {}
    try:
        exif = image._getexif()  
        if exif:
            for tag, value in exif.items():
                decoded_tag = TAGS.get(tag, tag)
                exif_data[decoded_tag] = value
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
    return exif_data

def get_gps_data(exif_data):
    """Extract GPS data from EXIF."""
    gps_data = {}
    if "GPSInfo" in exif_data:
        for key in exif_data["GPSInfo"].keys():
            decoded_key = GPSTAGS.get(key, key)
            gps_data[decoded_key] = exif_data["GPSInfo"][key]
    return gps_data

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees."""
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

def extract_metadata(image):
    """Extract relevant metadata (GPS and date) from the image."""
    exif_data = get_exif_data(image)
    gps_data = get_gps_data(exif_data)

    latitude = longitude = None
    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        latitude = convert_to_degrees(gps_data["GPSLatitude"])
        if gps_data["GPSLatitudeRef"] != "N":
            latitude = -latitude

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        longitude = convert_to_degrees(gps_data["GPSLongitude"])
        if gps_data["GPSLongitudeRef"] != "E":
            longitude = -longitude

    date_created = exif_data.get("DateTimeOriginal", "Unknown")

    return latitude, longitude, date_created

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        file_content = file.read()
        
        # Upload the image to Firebase Storage
        blob = bucket.blob(file.filename)
        blob.upload_from_file(io.BytesIO(file_content), content_type=file.content_type)

        # URL-encode the filename to handle spaces and special characters
        image_path = file.filename.replace(" ", "%20")
        image_url = f"https://firebasestorage.googleapis.com/v0/b/airecondrone.appspot.com/o/{image_path}?alt=media"

        # Prepare the image for metadata extraction
        img = Image.open(io.BytesIO(file_content))
        
        # Call your metadata extraction function here
        latitude, longitude, date_created = extract_metadata(img)

        # Save the image details to Firestore
        doc_ref = db.collection('images').add({
            'file_name': file.filename,
            'image_url': image_url,
            'latitude': latitude,
            'longitude': longitude,
            'date_created': date_created
        })

        _, doc_ref = doc_ref
        document_id = doc_ref.id  

        return jsonify({
            'document_id': document_id,
            'image_url': image_url,
            'latitude': latitude,
            'longitude': longitude,
            'date_created': date_created
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)