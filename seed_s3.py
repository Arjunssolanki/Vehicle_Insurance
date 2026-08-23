import boto3
import os

print("Connecting to LocalStack S3 gateway...")
s3 = boto3.client('s3', endpoint_url='http://127.0.0.1:4566')

print("Creating target bucket...")
s3.create_bucket(Bucket='my-model-mlopsproj')

print("Building directory trees...")
os.makedirs('artifact/08_23_2026_00_20_20/model_trainer/trained_model', exist_ok=True)

print("Writing local mock binaries...")
with open('artifact/08_23_2026_00_20_20/model_trainer/trained_model/model.pkl', 'wb') as f:
    f.write(b'mock_pickle_data')

print("Uploading files to the registry...")
s3.upload_file(
    'artifact/08_23_2026_00_20_20/model_trainer/trained_model/model.pkl', 
    'my-model-mlopsproj', 
    'model-registry/model.pkl'
)
print("LocalStack environment seeded successfully!")
