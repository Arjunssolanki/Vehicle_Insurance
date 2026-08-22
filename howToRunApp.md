# 🚀 Vehicle Insurance Prediction Application

This guide outlines the exact sequence required to spin up the local cloud infrastructure, seed the machine learning model artifacts, and run the FastAPI application from scratch when Docker and LocalStack are closed.

---

## 📋 Prerequisites

- Ensure **Docker Desktop** is open, running, and green on your machine.
- Ensure you are inside your project root working directory: `Vehicle_Insurance`

---

## 🛠️ Step-by-Step Execution Guide

### Step 1: Clean Terminal Paths & Activate Environment

Open a brand-new **PowerShell terminal window** and run the following command to strip rogue quotation marks from your Windows `PATH` and activate your virtual environment:

```powershell
env:PATH = env:PATH -replace '"', ''; conda activate vehicle
```

### Step 2: Inject LocalStack Session Variables

Configure your developer authorization token and redirect variables for this specific terminal instance:

```powershell
\$env:LOCALSTACK_AUTH_TOKEN="ls-mawO6638-LOWI-gIKu-TEZi-9312daLa04da"
\$env:IS_LOCAL="True"
\$env:AWS_ACCESS_KEY_ID="test"
\$env:AWS_SECRET_ACCESS_KEY="test"
\$env:REGION_NAME="us-east-1"
```

### Step 3: Launch LocalStack Pro Container

Spin up the LocalStack Pro engine background container directly via Docker to handle local cloud mocking:

```powershell
docker run -d --name localstack-main -p 4566:4566 -p 4510-4559:4510-4559 -e LOCALSTACK_AUTH_TOKEN="ls-mawO6638-LOWI-gIKu-TEZi-9312daLa04da" localstack/localstack-pro:latest
```

_(Wait 10–15 seconds for the mock cloud infrastructure services to initialize fully)._

### Step 4: Seed the Model Artifact File into S3 Bucket

Since LocalStack container volumes clear on fresh runs, execute this script to auto-generate the bucket and upload your existing `model.pkl` file into the target model registry directory path:

```powershell
python -c "import boto3; s3 = boto3.client('s3', endpoint_url='http://localhost:4566', aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1'); s3.create_bucket(Bucket='my-model-mlopsproj'); s3.upload_file(r'artifact\08_23_2026_00_20_20\model_trainer\trained_model\model.pkl', 'my-model-mlopsproj', 'model-registry/model.pkl')"
```

### Step 5: Boot Up Your FastAPI Web Server Application

Initialize your interactive Python server web gateway nodes:

```powershell
python app.py
```

### Step 6: Test Inferences Live on the Web Dashboard

1. Open your web browser and navigate directly to: **[http://127.0.0](http://127.0.0) (http://127.0.0.1:5000/)**
2. Fill out the vehicle profile feature matrices on the form.
3. Click **Submit** to process inputs and render your real-time **`Response-Yes`** or **`Response-No`** predictions smoothly!
