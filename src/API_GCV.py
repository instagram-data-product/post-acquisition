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


# Chargement des données de BigQuery
client = bigquery.Client()
query = "SELECT likes_num, caption, img_url, username FROM `instagram-scrapping-372812.your_dataset.Insta_Scrapping`"
query_job = client.query(query)
df_bigquery = query_job.to_dataframe()

# Chargement des images de Google Storage et extraction des caractéristiques avec Google Vision
client = gcs.Client()
bucket = client.get_bucket('instagram_scrapping_bucket')
images = bucket.list_blobs()
image_urls = [image.public_url for image in images]
client = vision_v1.ImageAnnotatorClient()
features = ['LABEL_DETECTION', 'FACE_DETECTION', 'IMAGE_PROPERTIES']

# Création d'un objet Feature pour chaque type de caractéristique
label_detection_feature = vision_v1.Feature(type=vision_v1.Feature.Type.LABEL_DETECTION)
face_detection_feature = vision_v1.Feature(type=vision_v1.Feature.Type.FACE_DETECTION)
image_properties_feature = vision_v1.Feature(type=vision_v1.Feature.Type.IMAGE_PROPERTIES)
features = [label_detection_feature, face_detection_feature, image_properties_feature]
image_labels = []
image_faces = []
image_colors = []
for url in image_urls:
   image = types.Image()
   image.source.image_uri = url
   response = client.annotate_image({'image': image, 'features': features})
image_labels = []
image_faces = []
image_colors = []
for url in image_urls:
    image = types.Image()
    image.source.image_uri = url
    response = client.annotate_image({'image': image, 'features': features})
    labels = [label.description for label in response.label_annotations]
    faces = len(response.face_annotations)
    colors = response.image_properties_annotation.dominant_colors
    image_labels.append(labels)
    image_faces.append(faces)
    image_colors.append(colors)


df_vision = pd.DataFrame({'img_url': image_urls, 'labels': image_labels, 'faces': image_faces, 'colors': image_colors})
df = pd.merge(df_bigquery, df_vision, on='img_url')
# On peut transformer les labels en variables binaires (1 si le label est présent, 0 sinon)
labels = pd.get_dummies(df['labels'].explode()).groupby(level=0).sum()
df_features = pd.concat([df[['faces']], labels], axis=1)
X = df_features.values
y = df['likes_num'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Mean squared error: ", mse)

# Chargement de l'image
#image_url = 'https://www.instagram.com/p/CpGvXHGD5Zm/'
#with urllib.request.urlopen(image_url) as url:
#image_content = url.read()
#image = types.Image(content=image_content)

# Extraction des caractéristiques avec Google Vision
#features = ['LABEL_DETECTION', 'FACE_DETECTION', 'IMAGE_PROPERTIES']
#client = vision_v1.ImageAnnotatorClient()
#response = client.annotate_image({'image': image, 'features': features})
#labels = [label.description for label in response.label_annotations]
#faces = len(response.face_annotations)
#colors = response.image_properties.dominant_colors.colors

# Transformation des caractéristiques en format utilisable par le modèle
#labels = pd.Series(labels).value_counts().reindex(columns=df_features.columns[1:], fill_value=0)
#features = pd.concat([pd.Series(faces), labels], axis=0).values.reshape(1, -1)

# Utilisation du modèle pour prédire le nombre de likes
#likes_pred = model.predict(features)[0]
#print("Nombre de likes prédit : ", likes_pred)
