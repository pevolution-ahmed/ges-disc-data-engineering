import os
from datetime import datetime
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from packages.ges_access.access_data import (
    _create_validation_files,
    _get_user_cridetials,
    _extract_earthdata,
    _create_temp_png_file
)
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator


urs = 'urs.earthdata.nasa.gov'    # Earthdata URL to call for authentication
homeDir = os.path.expanduser("~") + os.sep
username,password = _get_user_cridetials()
DATASET_NAME = 'ges_disc_air_temp_data'

with DAG(
    "my-first-dag",
    start_date=datetime(2022,8,1),
    schedule_interval="@once",
    catchup=False
    ) as dag:
    
    create_validation_files_task = PythonOperator(
        task_id = "create_validation_files",
        python_callable=_create_validation_files,
        op_args=[homeDir,urs,username,password]
    )
    extract_earthdata_task = PythonOperator(
        task_id = "extract_earthdata",
        python_callable=_extract_earthdata,
        op_args=[username,password]
    )
    create_temp_png_file = PythonOperator(
        task_id = "create_temp_png_file",
        python_callable=_create_temp_png_file,
    )
    create_bucket1 = GCSCreateBucketOperator(
        task_id="create_bucket1",
        bucket_name="source_files",
        location="US-CENTRAL1",
        labels={"env": "dev", "creator": "ahmed"},

    )
    upload_file = LocalFilesystemToGCSOperator(
        task_id="upload_file",
        src="./output_png_files/*",
        dst="/ges-disc/output_png_files/",
        bucket="source_files",
    )

    # Main Stream
    create_validation_files_task >> extract_earthdata_task >> create_temp_png_file >> create_bucket1 >> upload_file
