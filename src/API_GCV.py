# Py2+3 from __future__ import print_function
from google.cloud import vision
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:/ANNEE 5/Projet Instagram Scrapping/ServiceKey_GoogleCloud.json'

image_uri = 'gs://cloud-samples-data/vision/using_curl/shanghai.jpeg'

client = vision.ImageAnnotatorClient()
image = vision.Image() # Py2+3 if hasattr(vision, 'Image') else vision.types.Image()
image.source.image_uri = image_uri

response = client.label_detection(image=image)

print('Labels (and confidence score):')
print('=' * 30)
for label in response.label_annotations:
    print(label.description, '(%.2f%%)' % (label.score*100.))


