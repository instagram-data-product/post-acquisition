# Py2+3 from __future__ import print_function
from google.cloud import vision
from google.cloud import storage
import os
import google.cloud.storage as gcs
from google.cloud import bigquery
from google.cloud import vision_v1
from google.oauth2.service_account import Credentials
from google.cloud.vision_v1 import types, Feature
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
import hashlib
import pandas as pd
import urllib
import io

# Définir le chemin d'accès à votre clé d'authentification Google Cloud
os.environ[
    'GOOGLE_APPLICATION_CREDENTIALS'] = 'D:/Users/Paul/Documents/inge_3/projet_insta/key_google/ServiceKey_GoogleCloud.json'

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
                print(label[0], '(%.2f%%)' % (label[1] * 100))


# Initialiser les clients Google Cloud
client_vision = vision.ImageAnnotatorClient()
client_storage = storage.Client()
client_bigquery = bigquery.Client()

# Récupérer les données du bucket Google Storage
bucket = client_storage.get_bucket("instagram_scrapping_bucket")
images = bucket.list_blobs()


# Récupérer les données du BigQuery
query = "SELECT likes_num, caption, username, country, gs_uri, occupation, age FROM `instagram-scrapping-372812.your_dataset.Insta_Scrapping`"
df = client_bigquery.query(query).to_dataframe()
print(df)


# Extraire les fonctionnalités visuelles des images

features = []
for image in images:
    gs_uri = "gs://{}/{}".format(bucket.name, image.name)
    response = client_vision.annotate_image({
        'image': {'source': {'image_uri': gs_uri}},
        'features': [
            vision_v1.Feature(type=vision_v1.Feature.Type.LABEL_DETECTION),
            vision_v1.Feature(type=vision_v1.Feature.Type.FACE_DETECTION),
            vision_v1.Feature(type=vision_v1.Feature.Type.IMAGE_PROPERTIES)
        ]})
    labels = [label.description for label in response.label_annotations]
    faces = len(response.face_annotations)
    color = response.image_properties_annotation.dominant_colors.colors[0].color
    features.append({'gs_uri': gs_uri, 'labels': labels, 'faces': faces, 'color': color})

print(features[0])

# Convertir la liste des fonctionnalités des images en dataframe pandas
features_df = pd.DataFrame(features)
features_df['labels'] = features_df['labels'].apply(lambda x: ','.join(x))
print(features_df.head())

# Fusionner les données de la table avec les fonctionnalités des images en utilisant la colonne gs_uri comme clé de jointure
merged_df = pd.merge(df, features_df, on='gs_uri')
print(merged_df.head())

# Insérer les données fusionnées dans BigQuery
merged_df.to_gbq(destination_table='your_dataset.Insta_Scrapping_with_image_features', project_id='instagram-scrapping-372812', if_exists='replace')