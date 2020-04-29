from flask import Flask, render_template
from flask_uploads import UploadSet, IMAGES, configure_uploads
from forms import ImageForm, ChatForm
from werkzeug.utils import secure_filename
from datetime import datetime
import os 
from dlp_deidentification import deidentify_image_with_mask, deidentify_string_with_mask
from storage_interface import upload_blob

app = Flask(__name__)
app.config['SECRET_KEY'] = 'questadovrebbeessereunakeyseria'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(os.path.dirname(__file__), 'uploads')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# infoTypes I want to detect
INFO_TYPES=["FIRST_NAME", "LAST_NAME", "EMAIL_ADDRESS", "LOCATION", "ITALY_FISCAL_CODE"]

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)


@app.route('/img_upload', methods=['GET', 'POST'])
def img_upload():
    form = ImageForm()
    if form.validate_on_submit():
        recipient = []
        file = form.image.data
        username = form.username.data

        # QUARANTINE save temporary file 
        filename = secure_filename(file.filename)
        extended_filename = f"{UPLOAD_FOLDER}/{filename}"
        file.save(extended_filename)

        # REDACTION
        findings, redacted_image = deidentify_image_with_mask(extended_filename, INFO_TYPES)
        recipient = findings

        # UPLOAD to google cloud
        cloud_storage_filename = f"{username}_{filename}"
        cloud_storage_filename = f"redacted_{cloud_storage_filename}"
        try:
            upload_blob(extended_filename, cloud_storage_filename, is_redact=False)
            upload_blob(redacted_image, cloud_storage_filename, is_redact=True)
        except Exception as e:
            recipient.append(e)
        
        #delete temporary files
        os.remove(extended_filename)
        os.remove(redacted_image)
        return render_template('results.html', title='Results', recipient=recipient)
    return render_template('img_upload.html', title='Upload your image', form=form)

@app.route('/chat', methods=['GET', 'POST'])
def chat_room():
    form = ChatForm()
    if form.validate_on_submit():
        recipient = []
        username = form.username.data
        
        # QUARENTINE create temporary files
        timestamp = datetime.timestamp(datetime.now())
        filename = f"{username}_{timestamp}.txt"
        extended_filename = f"{UPLOAD_FOLDER}/{filename}"
        with open(extended_filename, "w+") as file:
            file.write(form.message.data)
        redacted_filename = f"redacted_{filename}"
        extend_redacted_filename = f"{UPLOAD_FOLDER}/{redacted_filename}"
        redacted_file = open(extend_redacted_filename, "w+")
        
        # REDACTION
        redacted_string = deidentify_string_with_mask(form.message.data, INFO_TYPES)
        recipient.append(redacted_string)
        redacted_file.write(redacted_string)
        redacted_file.close()

        # UPLOAD to google cloud
        try:
            upload_blob(extended_filename, filename, is_redact=False)
            upload_blob(extend_redacted_filename, redacted_filename, is_redact=True)
        except Exception as e:
            recipient.append(e)

        #delete temporary files
        os.remove(extended_filename)
        os.remove(extend_redacted_filename)
        return render_template('results.html', title='Results', recipient=recipient)
    return render_template('chat.html', title='Send your feedback', form=form)

# just for showing the results of the inspection of the image or of the string
@app.route('/results')
def results(recipient):
    return render_template('results.html', recipient=recipient, title='Results')

@app.route('/')
def home():
    return render_template('home.html', title='Help Center')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)