import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/superg28/projects/paydna-flask-upload-server/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app, resources=r'/upload')

def file_type(filename):
    print(filename.rsplit('.', 1)[1])

@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        file = request.files['myfile']
        print(file.filename)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded'
    else:
        return 'Uploads Found'