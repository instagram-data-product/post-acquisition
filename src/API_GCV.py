# Py2+3 from __future__ import print_function
from google.cloud import vision
from google.cloud import storage
import os
import google.cloud.storage as gcs
from google.cloud import bigquery
from google.cloud import vision_v1
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
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'D:/Users/Paul/Documents/inge_3/projet_insta/key_google/ServiceKey_GoogleCloud.json'

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


# Initialiser les clients Google Cloud
client_vision = vision.ImageAnnotatorClient()
client_storage = storage.Client()
client_bigquery = bigquery.Client()

# Récupérer les données du bucket Google Storage
bucket = client_storage.get_bucket("instagram_scrapping_bucket")
images = bucket.list_blobs()


# Récupérer les données du BigQuery
query = "SELECT likes_num, caption, img_url, username FROM `instagram-scrapping-372812.your_dataset.Insta_Scrapping`"
df = client_bigquery.query(query).to_dataframe()
# Créer une colonne unique pour chaque image en utilisant la fonction de hachage md5
df['image_id'] = df['img_url'].apply(lambda x: hashlib.md5(x.encode('utf-8')).hexdigest())
print(df)

# Extraire les fonctionnalités visuelles des images
features = []
for image in images:
    image_url = "gs://{}/{}".format(bucket.name, image.name)
    image_id = hashlib.md5(image_url.encode('utf-8')).hexdigest()
    response = client_vision.annotate_image({
                'image': {'source': {'image_uri': image_url}},
                'features': [
                    vision_v1.Feature(type=vision_v1.Feature.Type.LABEL_DETECTION),
                    vision_v1.Feature(type=vision_v1.Feature.Type.FACE_DETECTION),
                    vision_v1.Feature(type=vision_v1.Feature.Type.IMAGE_PROPERTIES)
                ]})
    labels = [label.description for label in response.label_annotations]
    faces = len(response.face_annotations)
    color = response.image_properties_annotation.dominant_colors.colors[0].color
    features.append({'image_id': image_id, 'image_url': image_url, 'labels': labels, 'faces': faces, 'color': color})

print(features[0])

df['image_url'] = df['img_url'].apply(lambda x: "gs://{}/{}".format(bucket.name, x))

# Extraire les fonctionnalités textuelles des données BigQuery
df['caption_length'] = df['caption'].apply(len)
df['has_hashtags'] = df['caption'].apply(lambda x: 1 if "#" in x else 0)
df['likes_num'] = df['likes_num'].str.replace("J’aime", "")
# Fusionner les données
df_test = df.merge(pd.DataFrame(features), on='image_url', how='left')

# Nettoyer les données
#df_test = df_test.drop_duplicates()
#df_test = df_test.dropna()

#print(df_test)
print(df_test["labels"])

""""
# Diviser les données en ensembles de formation et de test
X = df_test[['labels', 'faces', 'color', 'caption_length', 'has_hashtags']]
y = df_test['likes_num']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle de régression linéaire
model = LinearRegression()
model.fit(X_train, y_train)

# Évaluer le modèle
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)

"""
