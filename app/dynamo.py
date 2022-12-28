import boto3
import json
import yaml
import logging
import os
from datetime import datetime

from botocore.exceptions import ClientError

log = logging.getLogger(__name__)


def get_now_time():
    now = datetime.now() # current date and time
    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")
    return date_time


class DynamoDBConn:

    def __init__(self, config) -> None:
        self.config = config
        self.aws_access_key_id = self.config['access_key']
        self.aws_secret_access_key = self.config['secret_key']
        self.region = self.config['region']

        self.dynamodb = boto3.resource('dynamodb',
                            region_name=self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)
        self.client = boto3.client('dynamodb',
                            region_name=self.region,
                            aws_access_key_id=self.aws_access_key_id,
                            aws_secret_access_key=self.aws_secret_access_key)
        
        self.signup_table_name = 'UserInfo'
        self.chatlog_table_name = 'UserLog'

        # number of users

    # ===== create and delete tables START =====
    
    def create_signup_table(self):
        existing_tables = self.client.list_tables()['TableNames']
        if self.signup_table_name in existing_tables:
            return

        try:
            response = self.dynamodb.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'email_addr',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'password',
                        'AttributeType': 'S'
                    },
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': "PasswordIndex",
                        'KeySchema': [
                            {
                                'KeyType': 'HASH',
                                'AttributeName': 'password'
                            },
                            {
                                'KeyType': 'RANGE',
                                'AttributeName': 'email_addr'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'INCLUDE',
                            'NonKeyAttributes': ['avatar_path']
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 2,
                            'WriteCapacityUnits': 2
                        }
                    },
                ],
                TableName=self.signup_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'email_addr',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'username',
                        'KeyType': 'RANGE'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
        except ClientError as e:
            response = e.response

        return response
    
    def _delete_signup_table(self):
        try:
            response = self.client.delete_table(
                TableName=self.signup_table_name
            )
        except ClientError as e:
            response = e.response

        return response
    
    def create_chatlog_table(self):
        existing_tables = self.client.list_tables()['TableNames']
        if self.chatlog_table_name in existing_tables:
            return
        try:
            response = self.dynamodb.create_table(
                AttributeDefinitions=[
                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'email_addr',
                        'AttributeType': 'S'
                    },
                ],
                TableName=self.chatlog_table_name,
                KeySchema=[
                    {
                        'AttributeName': 'email_addr',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'username',
                        'KeyType': 'RANGE'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
        except ClientError as e:
            response = e.response

        return response
    
    def _delete_chatlog_table(self):
        try:
            response = self.client.delete_table(
                TableName=self.chatlog_table_name
            )
        except ClientError as e:
            response = e.response

        return response
    
    def clean_table(self):
        self._delete_signup_table()
        self._delete_chatlog_table()
    
    # ===== create and delete tables END =====

    # ===== userInfo START =====
    
    def userinfo_put_item(self, email_addr, username, password):
        table = self.dynamodb.Table(self.signup_table_name)
        avatar_path = os.path.join(username, "avatar.png")

        try:
            response = table.put_item(
                Item={
                    'email_addr': email_addr,
                    'username': username,
                    'password': password,
                    'avatar_path': avatar_path
                },
                ConditionExpression='attribute_not_exists(email_addr)'
            )
        except ClientError as e:
            response = e.response
            if response['Error']['Code'] == 'ConditionalCheckFailedException':
                log.error('This email has been used!')
            else:
                raise e

        # get status code by response['ResponseMetadata']['HTTPStatusCode']
        return response
    
    def _user_delete(self, email_addr, username):
        table = self.dynamodb.Table(self.signup_table_name)

        try:
            response = table.delete_item(Key={'email_addr': email_addr, 'username': username})
        except ClientError as e:
            response = e.response
        return response
    
    def userinfo_query(self, email_addr, password):
        table = self.dynamodb.Table(self.signup_table_name)

        try:
            response = table.query(
                IndexName="PasswordIndex",
                KeyConditionExpression="email_addr = :v1 AND password = :v2",
                ExpressionAttributeValues={
                    ":v1": email_addr,
                    ":v2": password
                },
            )

            records = []

            for i in response['Items']:
                records.append(i)

            return records
        except Exception as e:
            return str(e)
    
    def get_num_users(self):
        table = self.dynamodb.Table(self.signup_table_name)
        try:
            response = table.scan()
            items = response['Items']
            return len(items)
        except ClientError as e:
            return -1
    
    # ===== userInfo END =====

    # ===== userLog START =====

    def userlog_put_item(self, email_addr, username):
        table = self.dynamodb.Table(self.chatlog_table_name)
        chatlog_path = os.path.join(username, "chatlog.txt")

        try:
            response = table.put_item(
                Item={
                    'email_addr': email_addr,
                    'username': username,
                    'last_action_time': get_now_time(),
                    'chatlog_path': chatlog_path
                },
                ConditionExpression='attribute_not_exists(email_addr)'
            )
        except ClientError as e:
            response = e.response
            if response['Error']['Code'] == 'ConditionalCheckFailedException':
                log.error('This email has been used!')

        # get status code by response['ResponseMetadata']['HTTPStatusCode']
        return response
    
    def _chatlog_delete(self, email_addr, username):
        table = self.dynamodb.Table(self.chatlog_table_name)

        try:
            response = table.delete_item(Key={'email_addr': email_addr, 'username': username})
        except ClientError as e:
            response = e.response
        return response
    
    def userlog_query(self, email_addr, username):
        table = self.dynamodb.Table(self.chatlog_table_name)

        try:
            response = table.get_item(
            Key={
                    'email_addr': email_addr,
                    'username': username
                },
                ProjectionExpression = "email_addr, username, last_action_time, chatlog_path",
            )

            data = {}

            if 'Item' in response:
                item = response['Item']
                data.update(item)

            return data
        except Exception as e:
            return str(e)
    
    def update_userlog_last_action_time(self, email_addr, username):
        """
        update last action time to now
        """
        table = self.dynamodb.Table(self.chatlog_table_name)
        try:
            response = table.update_item(
                Key={
                    'email_addr': email_addr,
                    'username': username
                },
                UpdateExpression="set last_action_time = :r",
                ExpressionAttributeValues={
                    ':r': get_now_time(),
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            response = e.response
        return response

    def list_items(self):
        table = self.dynamodb.Table(self.chatlog_table_name)
        try:
            response = table.scan()
            items = response['Items']
            return items
        except ClientError as e:
            return

    # ===== userLog END =====

    # ===== common START =====

    def clean_user(self, email_addr, username):
        self._user_delete(email_addr, username)
        self._chatlog_delete(email_addr, username)

    # ===== common END =====
    