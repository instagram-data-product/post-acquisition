import glob
import os
from google.cloud import storage

#GCS_CLIENT = storage.Client()
def upload_from_directory(directory_path: str, dest_bucket_name: str, dest_blob_name: str):
    storage_client = storage.Client.from_service_account_json('ServiceKey_GoogleCloud.json')
    rel_paths = glob.glob(directory_path + '/**', recursive=True)
    bucket = storage_client.get_bucket(dest_bucket_name)
    #bucket = GCS_CLIENT.bucket(dest_bucket_name)
    for local_file in rel_paths:
        remote_path = f'{dest_blob_name}/{"/".join(local_file.split(os.sep)[1:])}'
        if os.path.isfile(local_file):
            blob = bucket.blob(remote_path)
            blob.upload_from_filename(local_file)

path_folder = r'Images'
gcs_path = "instagram_scrapping_bucket"
blob_name = "DossierImages2"

upload_from_directory(path_folder,gcs_path,blob_name)