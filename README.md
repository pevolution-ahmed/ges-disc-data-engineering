# GES DISC Data Engineering
**GES DISC**: is the home (archive) of NASA Precipitation and Hydrology, as well as Atmospheric Composition and Dynamics remote sensing data and information.

## Project Ideation (Problem Statement):
- Create a data Pipeline to extract and transform .nc4 files from nasa ges-disc to png images files , and then upload those files into GCS bucket using Apache Airflow.
## Environment Creation:
- Create a virtual environment using venv built in module in python
- Enter your virtual environment and setup 'requirements.txt' file as follows
    `pip install -r requirements.txt`
- Download the Cloud Provider connection SDK, in this project we use GCP
    - Install gcloud SDK to enable the gcloud cli in your terminal
    - use `gcloud init` command to initialize the connection
    - use `gcloud auth application-default login` to login into your account and create service account JSON file to be authinticated with the gcloud CLI.

## Data Description:
These datasets are about air temperature satellite data and it's an multidimensional geographic data.
## Project To-do:
- Use Airflow to execute on the following python callable functions:
    - Create Validation Files and Authenticate users to be able to use ges-disc API
    - Extract the data from ges-disc API.
    - Create png files using matplotlib to show the total air temperature of earth at a specific month
- Use An operator to upload the png files to Google Cloud Storage Bucket.
## Test Use cases:
- Test whether the username and the password is exists in the environment variables or not.
- Test the response of the session is coming back with status 200 or not.
## Transformation Output Sample:

![image](https://user-images.githubusercontent.com/43514480/187806676-e4daa8c4-0d2c-467a-b9a4-b5b31a805b05.png)
