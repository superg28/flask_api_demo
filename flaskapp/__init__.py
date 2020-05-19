import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from .aws_tools import detect_faces, detect_text

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
from flaskapp.api.users import usersbp

ID_UPLOAD_FOLDER = '/home/superg28/projects/paydna-flask-upload-server/uploads/id'
POA_UPLOAD_FOLDER = '/home/superg28/projects/paydna-flask-upload-server/uploads/poa'

app = Flask(__name__)
app.config['ID_UPLOAD_FOLDER'] = ID_UPLOAD_FOLDER
app.config['POA_UPLOAD_FOLDER'] = POA_UPLOAD_FOLDER

# register blueprints
app.register_blueprint(tutukabp)
app.register_blueprint(luhnbp)
app.register_blueprint(usersbp)

CORS(app, resources=r'/upload/*')

def file_type(filename):
    print(filename.rsplit('.', 1)[1])

@app.route('/upload/<string:endpoint>', methods=['GET', 'POST'])
def file_upload(endpoint):
    print(f"upload endpoint: {endpoint}")
    if request.method == 'POST':
        file = request.files['myfile']
        filebytes = file.stream.read()
        if endpoint == 'id':
            # if(detect_faces(file.stream.read())):
            if(detect_faces(filebytes)):
                # detect_text(filebytes)
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['ID_UPLOAD_FOLDER'], filename))
                return { "faceFound": True, "fileName": os.path.join(app.config['ID_UPLOAD_FOLDER'], filename) }
            else:
                return { "faceFound": False }
        elif endpoint == 'poa':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['POA_UPLOAD_FOLDER'], filename))
            return { "proofUploaded": True, "fileName": os.path.join(app.config['POA_UPLOAD_FOLDER'], filename) }
        else:
            return { 'ResultText': 'Endpoint not found'}
    else:
        return 'Uploads Found'

@app.route('/auth', methods=['POST'])
def authenticate():
    return { 'authentication': 'service' }