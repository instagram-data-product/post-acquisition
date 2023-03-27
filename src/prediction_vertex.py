import pandas as pd
from google.cloud import bigquery
from google.oauth2.service_account import Credentials

credentials = Credentials.from_service_account_file(
    'D:/ANNEE 5/Projet Instagram Scrapping/ServiceKey_GoogleCloud.json')

#Récupération et traitement des données:

# Instanciez un client BigQuery en utilisant vos informations d'identification
client = bigquery.Client(credentials=credentials)
# Définissez le nom de votre table BigQuery
table_id = "instagram-scrapping-372812.your_dataset.Insta_Scrapping_with_image_features"

# Écrivez une requête pour sélectionner les colonnes "likes_num" et "gs_uri" (et enlever les "j'aime")
query = f"""
SELECT gs_uri, REGEXP_REPLACE(likes_num, r'[^\d]', '') AS cleaned_likes_num
FROM `{table_id}`
"""

# Exécutez la requête et stockez les résultats dans un DataFrame pandas
df = client.query(query).to_dataframe()

# Convertissez la colonne "cleaned_likes_num" en entiers
df['cleaned_likes_num'] = pd.to_numeric(df['cleaned_likes_num'], errors='coerce', downcast='integer')

import os
os.chdir("D:/ANNEE 5/Projet Instagram Scrapping/post-acquisition/src/")
# Enregistrez le DataFrame dans un fichier CSV
csv_file = 'likes_and_image_uri_with_categories.csv'
df.to_csv(csv_file, index=False)

#Changement de la conne des likes pour avoir des cathégories (faible, moyen, élevé)
import pandas as pd
# Chargez le fichier CSV dans un DataFrame
df = pd.read_csv(csv_file)
# Définir les seuils pour les catégories
low_threshold = 300000
medium_threshold = 2500000

# Fonction pour convertir les entiers "likes" en catégories
def likes_to_category(likes):
    if likes < low_threshold:
        return 'bas'
    elif likes < medium_threshold:
        return 'moyen'
    else:
        return 'haut'

# Appliquer la fonction de conversion aux entiers "likes"
df['cleaned_likes_num'] = df['cleaned_likes_num'].apply(likes_to_category)
df = df.drop_duplicates()
# Enregistrez le nouveau DataFrame dans un nouveau fichier CSV
new_csv_file_path = 'likes_and_image_uri_with_categories.csv'
df.to_csv(new_csv_file_path, index=False)


#On exprte nos données vers GCS:

from google.cloud import storage
from google.oauth2 import service_account

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Upload a file to the specified GCS bucket."""
    credentials = service_account.Credentials.from_service_account_file('D:/ANNEE 5/Projet Instagram Scrapping/ServiceKey_GoogleCloud.json')
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.")

bucket_name = "instagram_scrapping_bucket"
source_file_name = "D:/ANNEE 5/Projet Instagram Scrapping/post-acquisition/src/likes_and_image_uri_with_categories.csv"
destination_blob_name = "likes_and_image_uri_with_categories.csv"

# Envoie du fichier CSV sur GCS
upload_blob(bucket_name, source_file_name, destination_blob_name)
