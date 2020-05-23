import os
from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# import some tools
from flaskapp.aws_tools import detect_faces, detect_text
from flaskapp.api.common import encrypt_str

# import and config logging
import logging
import logzero
from logzero import logger

LOG_FILE = '/home/superg28/projects/paydna-flask-upload-server/logs'
logzero.logfile(filename='logs/paydna-api.log', maxBytes=25e7, backupCount=4, loglevel=logging.DEBUG)
logFormat = logging.Formatter('%(asctime)s:%(module)s:%(lineno)d:%(levelname)s:%(message)s')
logzero.formatter(logFormat)

# import blueprints
import flaskapp.api.tutuka as tutuka
import flaskapp.api.luhn as luhn
import flaskapp.api.users as users
import flaskapp.api_jwt as jwt

UPLOAD_FOLDER_PREFIX = '/home/superg28/projects/paydna-flask-upload-server/uploads'
# ID_UPLOAD_FOLDER = ''.join([UPLOAD_FOLDER_PREFIX,'/id'])
ID_UPLOAD_FOLDER = UPLOAD_FOLDER_PREFIX + '/id'
POA_UPLOAD_FOLDER = ''.join([UPLOAD_FOLDER_PREFIX,'/poa'])

app = Flask(__name__)
# app.config['UPLOAD_FOLDER_PREFIX'] = UPLOAD_FOLDER_PREFIX
app.config['ID_UPLOAD_FOLDER'] = ID_UPLOAD_FOLDER
app.config['POA_UPLOAD_FOLDER'] = POA_UPLOAD_FOLDER

# register blueprints
app.register_blueprint(tutuka.bp)
app.register_blueprint(luhn.bp)
app.register_blueprint(users.bp)
app.register_blueprint(jwt.bp)

# init database connection
from flaskapp.mongodb import conn
db = conn.db_init()

CORS(app, resources=r'/upload/*')

def file_type(filename):
    print(filename.rsplit('.', 1)[1])

@app.route('/upload/<string:endpoint>', methods=['POST'])
def file_upload(endpoint):
    file = request.files['myfile']
    # read to bytes for image check and then 'rewind'
    filebytes = file.stream.read()
    file.stream.seek(0)
    # rewind end
    if endpoint == 'id':
        # if(detect_faces(file.stream.read())):
        if(detect_faces(filebytes)):
            # detect_text(filebytes)
            filename = secure_filename(file.filename)
            savepath = os.path.join(app.config['ID_UPLOAD_FOLDER'], filename)
            logger.info(savepath)
            file.save(savepath)
            # file.save(os.path.join(app.config['ID_UPLOAD_FOLDER'], filename))
            token = encrypt_str(os.path.join(app.config['ID_UPLOAD_FOLDER'], filename))
            return { "faceFound": True, "fileToken": token.decode() }
            file.close()
        else:
            return { "faceFound": False }
    elif endpoint == 'poa':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['POA_UPLOAD_FOLDER'], filename))
        token = encrypt_str(os.path.join(app.config['POA_UPLOAD_FOLDER'], filename))
        return { "proofUploaded": True, "fileToken": token.decode() }
    else:
        return { 'ResultText': 'Endpoint not found'}

@app.route('/user_files/<uid>/<string:filename>')
def user_files(uid=None, filename=None):
    return { 'uid': uid, 'filename': filename }

@app.route('/auth', methods=['POST'])
def authenticate():
    return { 'authentication': 'service' }