import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .aws_tools import detect_faces

# import and config logging
import logging
import logzero
from logzero import logger

LOG_FILE = '/home/superg28/projects/paydna-flask-upload-server/logs'
logzero.logfile(filename='logs/paydna-api.log', maxBytes=25e7, backupCount=4, loglevel=logging.DEBUG)
logFormat = logging.Formatter('%(asctime)s:%(module)s:%(lineno)d:%(levelname)s:%(message)s')
logzero.formatter(logFormat)

# import blueprints
from flaskapp.api.tutuka import tutukabp
from flaskapp.api.luhn import luhnbp

UPLOAD_FOLDER = '/home/superg28/projects/paydna-flask-upload-server/uploads'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# register blueprints
app.register_blueprint(tutukabp)
app.register_blueprint(luhnbp)

CORS(app, resources=r'/upload')

def file_type(filename):
    print(filename.rsplit('.', 1)[1])

@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    if request.method == 'POST':
        file = request.files['myfile']
        print(file.filename)
        if(detect_faces(file.stream.read())):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return { "status": "success", "message": "Face found, file saved" }
        else:
            return { "status": "fail", "message": "Face not found in file" }
    else:
        return 'Uploads Found'