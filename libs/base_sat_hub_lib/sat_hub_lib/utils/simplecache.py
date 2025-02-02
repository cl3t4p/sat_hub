from abc import ABC, abstractmethod
import os
import boto3
import botocore
import logging


class SimpleCache(ABC):

    def __init__(self, cache_folder):
        self.log = logging.getLogger(type(self).__name__)
        self.cache_folder = cache_folder
        if not os.path.exists(self.cache_folder):
            os.makedirs(self.cache_folder)

    @abstractmethod
    def get(self, key):
        pass


class S3Cache(SimpleCache):

    def __init__(self, cache_folder, bucket_name, region_name):
        super().__init__(cache_folder)
        self.s3_client = boto3.client(
            "s3",
            region_name=region_name,
            config=botocore.client.Config(signature_version=botocore.UNSIGNED),
        )
        self.bucket_name = bucket_name

    def get(self, key, local_filename):
        if not os.path.exists(local_filename):
            self.log.info(f"Cache miss : Downloading {key} to {local_filename}")
            self.s3_client.download_file(self.bucket_name, key, local_filename)
        else:
            self.log.info(f"Cache hit : {key}")
        return local_filename
