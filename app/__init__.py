from flask import Flask
import logging
import sys
import signal
import os
import json
import yaml
import requests

from app.dynamo import DynamoDBConn
from app.s3 import S3Conn

webapp = Flask(__name__)
log = logging.getLogger(__name__)
webapp.logger.setLevel(logging.INFO)


webapp.config.update(
    SECRET_KEY='this-is-a-secret-key',
    UPLOAD_FOLDER='app/static/userfiles',
    CONFIG_FOLDER='app/config',
    TEMP_FOLDER='app/static/tempfiles'
)

with open(os.path.join(webapp.config['CONFIG_FOLDER'], 'aws_config.yaml'), 'r') as f:
    aws_config_str = json.dumps(yaml.safe_load(f))
aws_config = json.loads(aws_config_str)

dynamodb = DynamoDBConn(config=aws_config)
dynamodb.create_signup_table()
dynamodb.create_chatlog_table()

s3 = S3Conn(config=aws_config)
s3.create_bucket()

def handler(signal, frame):
    webapp.logger.info("Chat Bot Server Terminated.")
    sys.exit(0)
signal.signal(signal.SIGINT, handler)

from app import main