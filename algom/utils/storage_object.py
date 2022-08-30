#!/usr/bin/env python
from algom.utils.client import storageClient


class storageObject():
    """Upload and download files to/from Google Cloud Storage (GCS).
        - get_blob_list
        - download_file
        - upload_file
        - read_file
        - write_file

    """
    def __init__(self):
        client = storageClient()
        self.client = client.storage_client

    def get_blob_list(self, bucket_name):
        """Lists all the blobs in a given bucket."""
        # Note: Client.list_blobs requires at least package version 1.17.0.
        blobs = self.client.list_blobs(bucket_name)
        blob_list = [blob.name for blob in blobs]
        return blob_list

    def download_file(
        self,
        bucket_name,
        storage_path,
        destination_filename,
        local_path=''
    ):
        """Download a file from GCS. Returns the same filename as the file in GCP.

        Args:
            bucket_name (str): Name of the GCS Bucket
            storage_path (str): GCS blob path and file name. Do not include the bucket name.
            destination_filename (str): Path and name of destination (local) file.
            local_path (str): Local directory path. Defaults to current working directory.

        Returns:
            String containing file directory and name

        """
        self.bucket_name = bucket_name
        self.storage_path = storage_path
        self.destination_filename = destination_filename
        self.local_path = local_path
        self.bucket = self.client.get_bucket(bucket_name)
        self.blob = self.bucket.blob(storage_path)
        self.blob.download_to_filename(local_path + destination_filename)
        print("Downloaded file from GCS to: {}".format(
            local_path + destination_filename))
        return local_path + destination_filename

    def upload_file(self, bucket_name, storage_path, source_file_name):
        """Upload a file to GCS.

        Params
        ------
        bucket_name:    str, Name of the GCS Bucket
        storage_path:      str, GCS file/blob path and name. Do not include
                        the bucket name.
        source_file_name: str, Path and name of source (local) file.
        """
        self.bucket_name = bucket_name
        self.storage_path = storage_path
        self.source_file_name = source_file_name
        self.bucket = self.client.get_bucket(bucket_name)
        self.blob = self.bucket.blob(storage_path)
        self.blob.upload_from_filename(source_file_name)
        return self.blob.public_url

    def read_file(self, bucket_name, filepath):
        self.bucket_name = bucket_name
        self.bucket = self.client.get_bucket(bucket_name)
        self.blob = self.bucket.get_blob(filepath)
        return self.blob.download_as_string()

    def write_file(self, text, bucket_name, filepath, if_exists):
        self.bucket = self.client.get_bucket(bucket_name)
        self.blob = self.bucket.blob(filepath)
        self.blob.upload_from_string(text)
        return self.blob.public_url
