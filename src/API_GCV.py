# Py2+3 from __future__ import print_function
from google.cloud import vision
from google.cloud import storage
import os

# Définir le chemin d'accès à votre clé d'authentification Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Chemin de votre clef json'

# Définir le nom de votre bucket
bucket_name = 'instagram_scrapping_bucket'

# Créer une instance de client Google Cloud Storage
storage_client = storage.Client()

# Obtenir la liste de tous les objets dans votre bucket
blobs = storage_client.list_blobs(bucket_name)

# Créer une instance de client Google Vision
vision_client = vision.ImageAnnotatorClient()
def analyser_image(uri):
    image = vision.Image()
    image.source.image_uri = uri
    response = vision_client.label_detection(image=image)
    labels = []
    for label in response.label_annotations:
        labels.append((label.description, label.score))
    return labels
def analyser_images(bucket_name):
    # Obtenir la liste de tous les objets dans votre bucket
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        # Vérifier si l'objet est une image (par exemple, vérifier si l'extension de fichier est .jpg ou .png)
        if blob.name.endswith('.jpg') or blob.name.endswith('.png'):
            # Analyser l'image avec l'API Google Vision
            uri = 'gs://' + bucket_name + '/' + blob.name
            labels = analyser_image(uri)
            # Afficher les étiquettes détectées pour l'image
            print('Labels for image', blob.name)
            for label in labels:
                print(label[0], '(%.2f%%)' % (label[1]*100))

analyser_images(bucket_name)

