import boto3
import json
import yaml
import logging
import os

from botocore.exceptions import ClientError

log = logging.getLogger(__name__)


class S3Conn:

    def __init__(self, config) -> None:
        self.config = config
        self.aws_access_key_id = self.config['access_key']
        self.aws_secret_access_key = self.config['secret_key']
        self.region = self.config['region']
        self.bucket_name = self.config['bucket_name']

        self.s3 = boto3.resource('s3',
                        region_name=self.region,
                        aws_access_key_id=self.aws_access_key_id,
                        aws_secret_access_key=self.aws_secret_access_key)
        self.client = boto3.client('s3',
                        region_name=self.region,
                        aws_access_key_id=self.aws_access_key_id,
                        aws_secret_access_key=self.aws_secret_access_key)
    
    def create_bucket(self):
        buckets = self.s3.buckets.all()
        if self.s3.Bucket(self.bucket_name) in buckets:
            return
        try:
            response = self.s3.create_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            response = e.response
        return response
    
    def upload_avatar(self, file_path, email_addr):
        """
        :param file_path: path of the file
        :param email_addr: the email address of user
        """
        s3_path = os.path.join(email_addr, "avatar.png")
        try:
            response = self.client.upload_file(file_path, self.bucket_name, s3_path)
        except ClientError as e:
            response = e.response
        return response
    
    def upload_chatlog(self, email_addr, text=''):
        binary_text = str.encode(text)
        s3_path = os.path.join(email_addr, "chatlog.txt")

        try:
            object = self.s3.Object(
                bucket_name=self.bucket_name, 
                key=s3_path
            )
            response = object.put(Body=binary_text)
        except ClientError as e:
            response = e.response
        return response
    
    def download_avatar(self, email_addr, local_path):
        """
        download the avatar locally

        :param email_addr: the name of the user
        :param local_path: path (folder/filename) of the file locally
        """
        s3_path = os.path.join(email_addr, "avatar.png")
        try:
            response = self.client.download_file(self.bucket_name, s3_path, local_path)
        except ClientError as e:
            response = e.response
        return response
    
    def download_chatlog(self, email_addr, local_path):
        s3_path = os.path.join(email_addr, "chatlog.txt")
        try:
            response = self.client.download_file(self.bucket_name, s3_path, local_path)
        except ClientError as e:
            response = e.response
        return response
    
    def delete_avatar(self, email_addr):
        s3_path = os.path.join(email_addr, "avatar.png")
        try:
            response = self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_path,
            )
        except ClientError as e:
            response = e.response
        return response
    
    def delete_chatlog(self, email_addr):
        s3_path = os.path.join(email_addr, "chatlog.txt")
        try:
            response = self.client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_path,
            )
        except ClientError as e:
            response = e.response
        return response
    
    def delete_folder(self, email_addr):
        """ 
        delete everything inside the folder, as well as folder itself
        """
        if 'Contents' not in self.client.list_objects(Bucket=self.bucket_name):
            logging.info('The bucket is already empty')
            return False

        bucket = self.s3.Bucket(self.bucket_name)
        bucket.objects.filter(Prefix="{}/".format(email_addr)).delete()
        logging.info('Delete the folder: {}'.format(email_addr))
        return True
