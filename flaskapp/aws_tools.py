import boto3
import json
import sys

def detect_faces(image_file_bytes):
    # check if face are detected in the upload
    client = boto3.client('rekognition')

    # with open(image_file, 'rb') as image:
    #     response = client.detect_faces(Image={'Bytes': image.read()}) 
    
    # change to a stream
    response = client.detect_faces(Image={'Bytes': image_file_bytes})

    # print('Detected faces for ' + image_file)    
    for faceDetail in response['FaceDetails']:
        # print('The detected face is between ' + str(faceDetail['AgeRange']['Low']) + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))

    # return len(response['FaceDetails'])
    return True if len(response['FaceDetails']) == 1 and response['FaceDetails'][0]['Confidence'] > 85.0 else False