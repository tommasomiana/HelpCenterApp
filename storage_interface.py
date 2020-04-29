from google.cloud import storage
import os

# you need a json file with your gcp credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= os.path.dirname(__file__) + "/tommisac.json"

# put two existing google cloud storage buckets here
PUBLIC_BUCKET = "public-bucket-pw2"
PRIVATE_BUCKET = "costumer-care-bucket-pw2"

def upload_blob(source_file_name, destination_blob_name, is_redact=False):
    """Uploads a file to the bucket.
        Args:
        source_file_name: The absolte filename of the file to upload.
        destination_blob_name: the name of the bucket where you want to store the file.
        is_redact: boolean which indicates if the filed as been redacted or not.
        PUBLIC_BUCKET and PRIVATE_BUCKET must be specified!
    Returns:
        None
    """
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    
    # storage the file in the right bucket
    bucket_name = PUBLIC_BUCKET if is_redact else PRIVATE_BUCKET
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
