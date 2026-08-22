import sys
from pandas import DataFrame
from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import MyException
from src.entity.estimator import MyModel
from src.logger import logging

class Proj1Estimator:
    """
    This class is used to save and retrieve our model from an S3 bucket (or LocalStack) 
    and to serve pipeline predictions.
    """

    def __init__(self, bucket_name: str, model_path: str):
        """
        :param bucket_name: Name of your model bucket (e.g., my-model-mlopsproj)
        :param model_path: Location key of your model inside the bucket
        """
        try:
            self.bucket_name = bucket_name
            self.s3 = SimpleStorageService()
            self.model_path = model_path
            self.loaded_model: MyModel = None
        except Exception as e:
            raise MyException(e, sys)

    def is_model_present(self, model_path: str = None) -> bool:
        """
        Checks if the model file exists in the active target bucket.
        """
        try:
            # Fallback to instance default if no custom path is provided
            check_path = model_path if model_path is not None else self.model_path
            return self.s3.s3_key_path_available(bucket_name=self.bucket_name, s3_key=check_path)
        except Exception as e:
            # Replaced print(e) with production custom exception tracking
            raise MyException(e, sys)

    def load_model(self) -> MyModel:
        """
        Loads and deserializes the model object from the specified bucket path.
        """
        try:
            logging.info(f"Loading model object from path: {self.model_path} in bucket: {self.bucket_name}")
            return self.s3.load_model(self.model_path, bucket_name=self.bucket_name)
        except Exception as e:
            raise MyException(e, sys) from e

    def save_model(self, from_file: str, remove: bool = False) -> None:
        """
        Saves the serialized model out to your target storage container.
        :param from_file: Your local file system source path (e.g., artifact/model.pkl)
        :param remove: If true, deletes the local source file after a successful upload.
        """
        try:
            logging.info(f"Uploading local model {from_file} to cloud path {self.model_path}")
            self.s3.upload_file(
                from_filename=from_file,
                to_filename=self.model_path,
                bucket_name=self.bucket_name,
                remove=remove
            )
        except Exception as e:
            raise MyException(e, sys) from e

    def predict(self, dataframe: DataFrame):
        """
        Pulls down the model instance automatically if needed and runs batch predictions.
        """
        try:
            if self.loaded_model is None:
                logging.info("Cached model instance empty. Initializing download sequence...")
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise MyException(e, sys) from e
