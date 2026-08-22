import sys
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run
import boto3

from typing import Optional

# Corrected package names spelling from 'pipline' to 'pipeline'
from src.constants import APP_HOST, APP_PORT, MODEL_BUCKET_NAME, MODEL_PUSHER_S3_KEY, MODEL_FILE_NAME
from src.pipline.prediction_pipeline import VehicleData, VehicleDataClassifier
from src.pipline.training_pipeline import TrainPipeline
from src.entity.s3_estimator import Proj1Estimator
from src.exception import MyException
from src.logger import logging

# Initialize FastAPI application
app = FastAPI()

# Mount the 'static' directory for serving static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 template engine for rendering HTML templates
templates = Jinja2Templates(directory='templates')

# Allow all origins for Cross-Origin Resource Sharing (CORS)
origins = ["*"]

# Configure middleware to handle CORS, allowing requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to safely hold your active model tracking engine
estimator = None

class DataForm:
    """
    DataForm class to handle and process incoming form data.
    This class handles converting raw browser strings into model-ready numbers.
    """
    def __init__(self, request: Request):
        self.request: Request = request
        self.Gender: Optional[int] = None
        self.Age: Optional[int] = None
        self.Driving_License: Optional[int] = None
        self.Region_Code: Optional[float] = None
        self.Previously_Insured: Optional[int] = None
        self.Annual_Premium: Optional[float] = None
        self.Policy_Sales_Channel: Optional[float] = None
        self.Vintage: Optional[int] = None
        self.Vehicle_Age_lt_1_Year: Optional[int] = None
        self.Vehicle_Age_gt_2_Years: Optional[int] = None
        self.Vehicle_Damage_Yes: Optional[int] = None
                
    async def get_vehicle_data(self):
        """
        Method to retrieve and assign form data to class attributes.
        Explicitly casts string text inputs to integers or floats safely.
        """
        form = await self.request.form()
        try:
            self.Gender = int(form.get("Gender")) if form.get("Gender") is not None else 0
            self.Age = int(form.get("Age")) if form.get("Age") is not None else 0
            self.Driving_License = int(form.get("Driving_License")) if form.get("Driving_License") is not None else 0
            self.Region_Code = float(form.get("Region_Code")) if form.get("Region_Code") is not None else 0.0
            self.Previously_Insured = int(form.get("Previously_Insured")) if form.get("Previously_Insured") is not None else 0
            self.Annual_Premium = float(form.get("Annual_Premium")) if form.get("Annual_Premium") is not None else 0.0
            self.Policy_Sales_Channel = float(form.get("Policy_Sales_Channel")) if form.get("Policy_Sales_Channel") is not None else 0.0
            self.Vintage = int(form.get("Vintage")) if form.get("Vintage") is not None else 0
            self.Vehicle_Age_lt_1_Year = int(form.get("Vehicle_Age_lt_1_Year")) if form.get("Vehicle_Age_lt_1_Year") is not None else 0
            self.Vehicle_Age_gt_2_Years = int(form.get("Vehicle_Age_gt_2_Years")) if form.get("Vehicle_Age_gt_2_Years") is not None else 0
            self.Vehicle_Damage_Yes = int(form.get("Vehicle_Damage_Yes")) if form.get("Vehicle_Damage_Yes") is not None else 0
        except Exception as e:
            raise Exception(f"Failed to process and cast numeric form variables: {str(e)}")


@app.on_event("startup")
def load_production_model():
    """
    Triggered automatically when the FastAPI server initializes.
    Ensures LocalStack infrastructure has our bucket and initializes the estimator layer.
    """
    global estimator
    try:
        # Automated LocalStack bucket verification layer 
        is_local = os.getenv("IS_LOCAL", "True").lower() == "true"
        if is_local:
            logging.info("Startup Check: Verifying LocalStack bucket infrastructure...")
            s3_client = boto3.client(
                "s3",
                endpoint_url="http://localhost:4566",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
                region_name="us-east-1"
            )
            # Create the bucket if a Docker reset wiped it out
            try:
                s3_client.head_bucket(Bucket=MODEL_BUCKET_NAME)
                logging.info(f"Verified bucket [{MODEL_BUCKET_NAME}] is already present.")
            except Exception:
                logging.info(f"Bucket [{MODEL_BUCKET_NAME}] missing from LocalStack. Auto-generating it now...")
                s3_client.create_bucket(Bucket=MODEL_BUCKET_NAME)

        # Initialize the global estimator tracking wrapper
        logging.info("API Startup: Connecting and initializing production model estimator...")
        s3_model_path = os.path.join(MODEL_PUSHER_S3_KEY, MODEL_FILE_NAME).replace("\\", "/")
        estimator = Proj1Estimator(bucket_name=MODEL_BUCKET_NAME, model_path=s3_model_path)
        logging.info("API Startup: Estimator engine loaded successfully.")
        
    except Exception as e:
        logging.error(f"Failed to load the model during server startup initialization: {str(e)}")
        raise MyException(e, sys)


# Route to render the main page with the form
@app.get("/", tags=["authentication"])
async def index(request: Request):
    """
    Renders the main HTML form page for vehicle data input.
    """
    return templates.TemplateResponse(
        request,
        "vehicledata.html",
        {"context": "Rendering"}
    )

# Route to trigger the model training process
@app.get("/train")
async def trainRouteClient():
    """
    Endpoint to initiate the model training pipeline.
    """
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        return Response("Training successful!!!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")

# Route to handle form submission and make predictions
@app.post("/")
async def predictRouteClient(request: Request):
    """
    Endpoint to receive form data, process it, and make a prediction.
    """
    try:
        form = DataForm(request)
        await form.get_vehicle_data()
        
        vehicle_data = VehicleData(
            Gender=form.Gender,
            Age=form.Age,
            Driving_License=form.Driving_License,
            Region_Code=form.Region_Code,
            Previously_Insured=form.Previously_Insured,
            Annual_Premium=form.Annual_Premium,
            Policy_Sales_Channel=form.Policy_Sales_Channel,
            Vintage=form.Vintage,
            Vehicle_Age_lt_1_Year=form.Vehicle_Age_lt_1_Year,
            Vehicle_Age_gt_2_Years=form.Vehicle_Age_gt_2_Years,
            Vehicle_Damage_Yes=form.Vehicle_Damage_Yes
        )

        # Convert form data into a DataFrame for the model
        vehicle_df = vehicle_data.get_vehicle_input_data_frame()

        # Initialize the prediction pipeline
        model_predictor = VehicleDataClassifier()

        # Make a prediction and retrieve the result scalar safely
        prediction_result = model_predictor.predict(dataframe=vehicle_df)
        
        # Extract individual prediction value scalar integer (0 or 1)
        value = prediction_result[0] if hasattr(prediction_result, "__getitem__") else prediction_result

        # Interpret the prediction result as 'Response-Yes' or 'Response-No'
        status = "Response-Yes" if int(value) == 1 else "Response-No"

        return templates.TemplateResponse(
            request,
            "vehicledata.html",
            {"context": status}
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}

# Main entry point to start the FastAPI server
if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
