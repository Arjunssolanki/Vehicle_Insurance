import os
import sys
import boto3
from src.constants import AWS_SECRET_ACCESS_KEY_ENV_KEY, AWS_ACCESS_KEY_ID_ENV_KEY, REGION_NAME
from src.exception import MyException
from src.logger import logging

class S3Client:
    s3_client = None
    s3_resource = None

    def __init__(self, region_name=REGION_NAME):
        """ 
        This Class gets aws credentials from env_variable and creates a connection with an S3 bucket.
        It redirects to LocalStack if the IS_LOCAL environment variable is set to True.
        """
        try:
            if S3Client.s3_resource is None or S3Client.s3_client is None:
                __access_key_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY)
                __secret_access_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY)
                
                if __access_key_id is None:
                    raise Exception(f"Environment variable: {AWS_ACCESS_KEY_ID_ENV_KEY} is not set.")
                if __secret_access_key is None:
                    raise Exception(f"Environment variable: {AWS_SECRET_ACCESS_KEY_ENV_KEY} is not set.")
                
                # Check if running locally with LocalStack
                is_local = os.getenv("IS_LOCAL", "True").lower() == "true"
                
                if is_local:
                    logging.info("Connecting S3Client to LocalStack (http://localhost:4566)...")
                    localstack_url = "http://localhost:4566"
                    
                    S3Client.s3_resource = boto3.resource(
                        's3',
                        endpoint_url=localstack_url,
                        aws_access_key_id=__access_key_id,
                        aws_secret_access_key=__secret_access_key,
                        region_name=region_name
                    )
                    S3Client.s3_client = boto3.client(
                        's3',
                        endpoint_url=localstack_url,
                        aws_access_key_id=__access_key_id,
                        aws_secret_access_key=__secret_access_key,
                        region_name=region_name
                    )
                else:
                    logging.info("Connecting S3Client to live production AWS Cloud...")
                    S3Client.s3_resource = boto3.resource(
                        's3',
                        aws_access_key_id=__access_key_id,
                        aws_secret_access_key=__secret_access_key,
                        region_name=region_name
                    )
                    S3Client.s3_client = boto3.client(
                        's3',
                        aws_access_key_id=__access_key_id,
                        aws_secret_access_key=__secret_access_key,
                        region_name=region_name
                    )
            
            self.s3_resource = S3Client.s3_resource
            self.s3_client = S3Client.s3_client
            
        except Exception as e:
            raise MyException(e, sys)
